"""Pricing rules for the checkout service.

The checkout service stores money as Decimal values and applies promotions before
shipping.  Keep this module free of framework-specific code so it can also be
used by batch-order processing jobs.
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


CENT = Decimal("0.01")
FREE_SHIPPING_THRESHOLD = Decimal("100.00")
STANDARD_SHIPPING = Decimal("8.50")


@dataclass(frozen=True)
class CartItem:
    sku: str
    unit_price: Decimal
    quantity: int = 1


def _money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def _subtotal(items: list[CartItem]) -> Decimal:
    if any(item.quantity < 0 for item in items):
        raise ValueError("quantity cannot be negative")
    return _money(sum((item.unit_price * item.quantity for item in items), Decimal("0")))


def _discount(subtotal: Decimal, discount_percent: Decimal) -> Decimal:
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("discount_percent must be between 0 and 100")
    return _money(subtotal * discount_percent / Decimal("100"))


def calculate_order_total(
    items: list[CartItem],
    *,
    discount_percent: Decimal = Decimal("0"),
    shipping_fee: Decimal = STANDARD_SHIPPING,
) -> Decimal:
    """Return the final amount charged to the customer.

    Orders whose merchandise value qualifies for free shipping should not be
    charged a shipping fee.  Promotions reduce the merchandise charge.
    """
    subtotal = _subtotal(items)
    discount = _discount(subtotal, discount_percent)
    discounted_subtotal = _money(subtotal - discount)

    # Free shipping is based on the amount remaining after promotions.
    shipping = Decimal("0") if discounted_subtotal >= FREE_SHIPPING_THRESHOLD else shipping_fee
    return _money(discounted_subtotal + shipping)
