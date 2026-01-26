import argparse
from typing import Optional

## Removed ensure_sqlite_schema import; not needed for Postgres
from backend.persistance.base import get_sessionmaker
from sqlalchemy import select, func


def ensure_schema() -> None:
    pass  # No-op for Postgres


def seed_categories() -> bool:
    from backend.persistance.category import Category
    from backend.persistance.subcategory import Subcategory
    from backend.scripts import seed_categories as _seed
    Session = get_sessionmaker()
    with Session() as s:
        cat_count = s.execute(select(func.count(Category.category_id))).scalar() or 0
        sub_count = s.execute(select(func.count(Subcategory.subcategory_id))).scalar() or 0
    if cat_count == 0 or sub_count == 0:
        _seed.main()
        return True
    return False


def seed_users() -> bool:
    """
    Always run demo seeding. The seeder is idempotent by deterministic emails
    and will create any missing demo accounts up to configured counts.
    """
    from backend.scripts import seed_demo_data as _seed
    _seed.main()
    return True


def generate_images() -> int:
    from backend.scripts import generate_missing_category_images as _gen
    # Idempotent; will skip existing
    _gen.main()
    # We cannot easily get count here without parsing stdout; return -1 as n/a
    return -1


def assign_images() -> None:
    from backend.scripts import assign_images as _assign
    _assign.main()


def clear_products() -> None:
    from backend.scripts import clear_products as _clear
    _clear.main()


def run(all: bool = False,
        ensure: bool = False,
        seed_cats: bool = False,
        gen_imgs: bool = False,
        assign_imgs: bool = False,
        seed_demo_users: bool = False,
        reset_catalog: bool = False) -> None:
    if all:
        ensure = True
        seed_cats = True
        gen_imgs = True
        assign_imgs = True
        seed_demo_users = True
        # "all" does NOT clear products by default

    if ensure:
        ensure_schema()

    changed = False
    if seed_cats:
        changed = seed_categories() or changed

    if gen_imgs:
        generate_images()

    if assign_imgs:
        assign_images()

    if seed_demo_users:
        seed_users()

    if reset_catalog:
        clear_products()

    print("Bootstrap complete.")


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Unified bootstrap utility")
    parser.add_argument("--all", action="store_true", help="Run common dev bootstrap: schema, seed categories (if empty), generate+assign images, seed demo users (if empty)")
    parser.add_argument("--ensure-schema", action="store_true", help="Ensure local schema")
    parser.add_argument("--seed-categories", action="store_true", help="Seed categories/subcategories if missing")
    parser.add_argument("--generate-images", action="store_true", help="Generate placeholder images for missing categories/subcategories")
    parser.add_argument("--assign-images", action="store_true", help="Assign images to categories/subcategories/users")
    parser.add_argument("--seed-users", action="store_true", help="Seed demo users if none exist")
    parser.add_argument("--reset-catalog", action="store_true", help="Delete all products and related records")
    args = parser.parse_args(argv)

    run(
        all=args.all,
        ensure=args.ensure_schema,
        seed_cats=args.seed_categories,
        gen_imgs=args.generate_images,
        assign_imgs=args.assign_images,
        seed_demo_users=args.seed_users,
        reset_catalog=args.reset_catalog,
    )


if __name__ == "__main__":
    main()
