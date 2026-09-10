from decimal import Decimal

import pytest

from order_engine.pricing import CartItem, calculate_order_total


def item(price: str, quantity: int = 1) -> CartItem:
    return CartItem("SKU-1", Decimal(price), quantity)


def test_standard_shipping_is_added_below_threshold():
    assert calculate_order_total([item("50.00")]) == Decimal("58.50")


def test_shipping_is_free_at_threshold_without_discount():
    assert calculate_order_total([item("100.00")]) == Decimal("100.00")


def test_percentage_discount_is_applied():
    assert calculate_order_total([item("50.00")], discount_percent=Decimal("10")) == Decimal("53.50")


def test_multiple_quantities_are_included_in_subtotal():
    assert calculate_order_total([item("20.00", 3)]) == Decimal("68.50")


def test_empty_cart_only_pays_configured_shipping():
    assert calculate_order_total([], shipping_fee=Decimal("5.00")) == Decimal("5.00")


def test_negative_quantity_is_rejected():
    with pytest.raises(ValueError, match="quantity"):
        calculate_order_total([item("10.00", -1)])


def test_invalid_discount_is_rejected():
    with pytest.raises(ValueError, match="discount_percent"):
        calculate_order_total([item("10.00")], discount_percent=Decimal("101"))
