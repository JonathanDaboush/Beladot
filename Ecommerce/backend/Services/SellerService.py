from Models.Seller import Seller
from Models.SellerFinance import SellerFinance
from Repositories.SellerRepository import SellerRepository
from Repositories.SellerFinanceRepository import SellerFinanceRepository


class SellerService:
    def __init__(self, seller_repo: SellerRepository, finance_repo: SellerFinanceRepository, audit_repo=None):
        self.seller_repo = seller_repo
        self.finance_repo = finance_repo
        self.audit_repo = audit_repo

    async def calculate_earnings(self, seller_id: int, start_date, end_date, order_repo, order_item_repo, return_repo, refund_repo, actor_id=None, actor_type='system', actor_email=None, ip_address=None, user_agent=None) -> dict:
        """
        Calculate total earnings for a seller between two dates, excluding returned/refunded items.
        Only includes delivered orders, and items not returned/refunded.
        Returns dict: { 'seller_earnings': int, 'company_profit': int, 'gross_sales': int }
        """
        PLATFORM_FEE = 0.20
        # Get all delivered orders in date range
        orders = await order_repo.get_orders_by_seller_and_status(seller_id, 'delivered', start_date, end_date)
        order_ids = [o.id for o in orders]
        if not order_ids:
            result = {'seller_earnings': 0, 'company_profit': 0, 'gross_sales': 0}
            if self.audit_repo:
                await self.audit_repo.create({
                    'actor_id': actor_id,
                    'actor_type': actor_type,
                    'actor_email': actor_email,
                    'action': 'calculate_earnings',
                    'target_type': 'seller',
                    'target_id': str(seller_id),
                    'item_metadata': {'result': result, 'start_date': str(start_date), 'end_date': str(end_date)},
                    'ip_address': ip_address,
                    'user_agent': user_agent
                })
            return result
        # Get all order items for these orders and this seller
        items = await order_item_repo.get_by_orders_and_seller(order_ids, seller_id)
        # Exclude items that are returned or refunded
        returned_item_ids = await return_repo.get_returned_item_ids(order_ids)
        refunded_item_ids = await refund_repo.get_refunded_item_ids(order_ids)
        gross_sales = 0
        seller_earnings = 0
        company_profit = 0
        for item in items:
            if item.id not in returned_item_ids and item.id not in refunded_item_ids:
                gross_sales += item.total_price_cents
                company_profit += int(item.total_price_cents * PLATFORM_FEE)
                seller_earnings += int(item.total_price_cents * (1 - PLATFORM_FEE))
        result = {
            'seller_earnings': seller_earnings,
            'company_profit': company_profit,
            'gross_sales': gross_sales
        }
        if self.audit_repo:
            await self.audit_repo.create({
                'actor_id': actor_id,
                'actor_type': actor_type,
                'actor_email': actor_email,
                'action': 'calculate_earnings',
                'target_type': 'seller',
                'target_id': str(seller_id),
                'item_metadata': {'result': result, 'start_date': str(start_date), 'end_date': str(end_date)},
                'ip_address': ip_address,
                'user_agent': user_agent
            })
        return result

    async def trigger_payout(self, seller_id: int, payout_date, order_repo, order_item_repo, return_repo, refund_repo, payout_repo, company_bank_repo=None, actor_id=None, actor_type='system', actor_email=None, ip_address=None, user_agent=None):
        """
        Create a SellerPayout for all eligible sales (delivered, return window closed, not returned/refunded, not already paid out).
        Marks items/orders as paid out. Also, calculate and record company profit (20% fee).
        """
        PLATFORM_FEE = 0.20
        # Get all delivered orders for this seller where return window is closed
        orders = await order_repo.get_eligible_for_payout(seller_id, payout_date)
        order_ids = [o.id for o in orders]
        if not order_ids:
            if self.audit_repo:
                await self.audit_repo.create({
                    'actor_id': actor_id,
                    'actor_type': actor_type,
                    'actor_email': actor_email,
                    'action': 'trigger_payout',
                    'target_type': 'seller',
                    'target_id': str(seller_id),
                    'item_metadata': {'reason': 'no eligible orders', 'payout_date': str(payout_date)},
                    'ip_address': ip_address,
                    'user_agent': user_agent
                })
            return None
        # Get all order items for these orders and this seller
        items = await order_item_repo.get_by_orders_and_seller(order_ids, seller_id)
        # Exclude items that are returned, refunded, or already paid out
        returned_item_ids = await return_repo.get_returned_item_ids(order_ids)
        refunded_item_ids = await refund_repo.get_refunded_item_ids(order_ids)
        eligible_items = [item for item in items if item.id not in returned_item_ids and item.id not in refunded_item_ids and not getattr(item, 'paid_out', False)]
        if not eligible_items:
            if self.audit_repo:
                await self.audit_repo.create({
                    'actor_id': actor_id,
                    'actor_type': actor_type,
                    'actor_email': actor_email,
                    'action': 'trigger_payout',
                    'target_type': 'seller',
                    'target_id': str(seller_id),
                    'item_metadata': {'reason': 'no eligible items', 'payout_date': str(payout_date)},
                    'ip_address': ip_address,
                    'user_agent': user_agent
                })
            return None
        total = sum(item.total_price_cents for item in eligible_items)
        seller_earnings = int(total * (1 - PLATFORM_FEE))
        company_profit = int(total * PLATFORM_FEE)
        related_order_ids = ','.join(str(item.order_id) for item in eligible_items)
        # Create payout record for seller
        from Models.SellerPayout import SellerPayout
        payout = SellerPayout(
            seller_id=seller_id,
            amount=seller_earnings / 100.0,  # store as decimal dollars
            payout_date=payout_date,
            status='pending',
            related_order_ids=related_order_ids,
            created_at=payout_date,
            updated_at=payout_date
        )
        payout = await payout_repo.create(payout)
        # Optionally, record company profit to company bank account (if repo provided)
        if company_bank_repo:
            company_account = await company_bank_repo.get_main_account()
            # Here you would record a transaction to the company account for company_profit
            # (Implementation depends on your accounting/ledger system)
        # Mark items as paid out (requires paid_out field on OrderItem)
        for item in eligible_items:
            item.paid_out = True
            await order_item_repo.update(item)
        if self.audit_repo:
            await self.audit_repo.create({
                'actor_id': actor_id,
                'actor_type': actor_type,
                'actor_email': actor_email,
                'action': 'trigger_payout',
                'target_type': 'seller',
                'target_id': str(seller_id),
                'item_metadata': {
                    'payout_id': getattr(payout, 'id', None),
                    'seller_earnings': seller_earnings,
                    'company_profit': company_profit,
                    'total_sales': total,
                    'related_order_ids': related_order_ids,
                    'payout_date': str(payout_date)
                },
                'ip_address': ip_address,
                'user_agent': user_agent
            })
        return payout

    async def register_seller(self, user_id: int, business_info: dict, finance_info: dict, actor_id=None, actor_type='system', actor_email=None, ip_address=None, user_agent=None) -> Seller:
        seller = Seller(
            user_id=user_id,
            legal_business_name=business_info['legal_business_name'],
            business_type=business_info['business_type'],
            phone_number=business_info['phone_number'],
            business_address=business_info['business_address'],
            tax_id=business_info['tax_id'],
            tax_country=business_info['tax_country'],
            is_verified=False,
            verification_submitted_at=None,
            verified_at=None,
            created_at=None,
            updated_at=None
        )
        seller = await self.seller_repo.create(seller)
        finance = SellerFinance(
            seller_id=seller.id,
            bank_account_number=finance_info['bank_account_number'],
            bank_routing_number=finance_info['bank_routing_number'],
            account_holder_name=finance_info['account_holder_name'],
            bank_country=finance_info['bank_country'],
            payout_frequency=finance_info.get('payout_frequency', 'weekly'),
            document_type=finance_info.get('document_type'),
            document_url=finance_info.get('document_url'),
            document_verified=False,
            created_at=None,
            updated_at=None
        )
        await self.finance_repo.create(finance)
        if self.audit_repo:
            await self.audit_repo.create({
                'actor_id': actor_id,
                'actor_type': actor_type,
                'actor_email': actor_email,
                'action': 'register_seller',
                'target_type': 'seller',
                'target_id': str(seller.id),
                'item_metadata': {'business_info': business_info, 'finance_info': {k: v for k, v in finance_info.items() if k != 'bank_account_number' and k != 'bank_routing_number'}},
                'ip_address': ip_address,
                'user_agent': user_agent
            })
        return seller

    async def get_seller_by_user(self, user_id: int, actor_id=None, actor_type='system', actor_email=None, ip_address=None, user_agent=None) -> Seller:
        seller = await self.seller_repo.get_by_user_id(user_id)
        if self.audit_repo:
            await self.audit_repo.create({
                'actor_id': actor_id,
                'actor_type': actor_type,
                'actor_email': actor_email,
                'action': 'get_seller_by_user',
                'target_type': 'seller',
                'target_id': str(getattr(seller, 'id', 'unknown')),
                'item_metadata': {'user_id': user_id},
                'ip_address': ip_address,
                'user_agent': user_agent
            })
        return seller

    async def get_seller_finance(self, seller_id: int, actor_id=None, actor_type='system', actor_email=None, ip_address=None, user_agent=None) -> SellerFinance:
        finance = await self.finance_repo.get_by_seller_id(seller_id)
        if self.audit_repo:
            await self.audit_repo.create({
                'actor_id': actor_id,
                'actor_type': actor_type,
                'actor_email': actor_email,
                'action': 'get_seller_finance',
                'target_type': 'seller',
                'target_id': str(seller_id),
                'item_metadata': {},
                'ip_address': ip_address,
                'user_agent': user_agent
            })
        return finance
