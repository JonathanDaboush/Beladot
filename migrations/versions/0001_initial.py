"""
Initial Alembic migration script.
"""
from alembic import op
import sqlalchemy as sa
# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None
def upgrade():
    # Create core catalog + user tables in the correct dependency order
    # 1) Category
    op.create_table(
        'category',
        sa.Column('category_id', sa.BigInteger, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('image_url', sa.String(255)),
    )

    # 2) Subcategory (FK -> category)
    op.create_table(
        'subcategory',
        sa.Column('subcategory_id', sa.BigInteger, primary_key=True),
        sa.Column('category_id', sa.BigInteger, sa.ForeignKey('category.category_id')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('image_url', sa.String(255)),
    )

    # 3) User
    op.create_table(
        'user',
        sa.Column('user_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('dob', sa.Date),
        sa.Column('password', sa.String(255), nullable=False),
        sa.Column('phone_number', sa.String(20)),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('created_at', sa.Date),
        sa.Column('img_location', sa.String(255)),
        sa.Column('account_status', sa.String(5), nullable=False, server_default='True'),
    )

    # 4) Product (FK -> user, category, subcategory)
    op.create_table(
        'product',
        sa.Column('product_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('seller_id', sa.BigInteger, sa.ForeignKey('user.user_id')),
        sa.Column('category_id', sa.BigInteger, sa.ForeignKey('category.category_id')),
        sa.Column('subcategory_id', sa.BigInteger, sa.ForeignKey('subcategory.subcategory_id')),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('price', sa.Numeric(10, 2)),
        sa.Column('currency', sa.String(10)),
        sa.Column('is_active', sa.Boolean, server_default=sa.text('TRUE')),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
    )

    # 4b) Product Image (FK -> product)
    op.create_table(
        'product_image',
        sa.Column('image_id', sa.BigInteger, primary_key=True),
        sa.Column('product_id', sa.BigInteger, sa.ForeignKey('product.product_id')),
        sa.Column('image_url', sa.String(255)),
    )

    # 5) Product Variant (FK -> product)
    op.create_table(
        'product_variant',
        sa.Column('variant_id', sa.BigInteger, primary_key=True),
        sa.Column('product_id', sa.BigInteger, sa.ForeignKey('product.product_id')),
        sa.Column('variant_name', sa.String(100)),
        sa.Column('price', sa.Numeric(10, 2)),
        sa.Column('quantity', sa.Integer),
        sa.Column('is_active', sa.Boolean, server_default=sa.text('TRUE')),
    )

    # 6) Cart (FK -> user)
    op.create_table(
        'cart',
        sa.Column('cart_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.BigInteger, sa.ForeignKey('user.user_id')),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
    )

    # 7) Cart Item (FK -> cart, product, product_variant)
    op.create_table(
        'cart_item',
        sa.Column('cart_item_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('cart_id', sa.BigInteger, sa.ForeignKey('cart.cart_id')),
        sa.Column('product_id', sa.BigInteger, sa.ForeignKey('product.product_id')),
        sa.Column('variant_id', sa.BigInteger, sa.ForeignKey('product_variant.variant_id'), nullable=True),
        sa.Column('quantity', sa.Integer),
    )

def downgrade():
    op.drop_table('product_image')
    op.drop_table('cart_item')
    op.drop_table('cart')
    op.drop_table('product_variant')
    op.drop_table('product')
    op.drop_table('user')
    op.drop_table('subcategory')
    op.drop_table('category')
