import { useEffect } from 'react';
import useCartStore from '../store/cartStore';
import styles from './Cart.module.css';

const Cart = () => {
  const { cart, loading, error, fetchCart, updateItem, removeItem, clearCart } = useCartStore();

  useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  const handleQuantityChange = async (itemId: string, newQuantity: number) => {
    if (newQuantity < 1) return;
    try {
      await updateItem(itemId, newQuantity);
    } catch (err) {
      console.error('Failed to update item:', err);
    }
  };

  const handleRemoveItem = async (itemId: string) => {
    try {
      await removeItem(itemId);
    } catch (err) {
      console.error('Failed to remove item:', err);
    }
  };

  const handleClearCart = async () => {
    if (window.confirm('Вы уверены, что хотите очистить корзину?')) {
      try {
        await clearCart();
      } catch (err) {
        console.error('Failed to clear cart:', err);
      }
    }
  };

  if (loading && !cart) {
    return <div className={styles.loading}>Загрузка корзины...</div>;
  }

  if (error) {
    return <div className={styles.error}>Ошибка: {error}</div>;
  }

  const items = cart?.items || [];
  const summary = cart?.summary || { total_items: 0, total_price: 0 };

  return (
    <div className={styles.cart}>
      <div className={styles.header}>
        <h1>Корзина</h1>
        {items.length > 0 && (
          <button onClick={handleClearCart} className={styles.clearButton}>
            Очистить корзину
          </button>
        )}
      </div>

      {items.length === 0 ? (
        <p className={styles.empty}>Ваша корзина пуста</p>
      ) : (
        <>
          <div className={styles.items}>
            {items.map((item) => (
              <div key={item.id} className={styles.item}>
                <div className={styles.itemInfo}>
                  <h3>{item.product_name}</h3>
                  {item.sku_attributes && (
                    <p className={styles.attributes}>
                      {Object.entries(item.sku_attributes).map(([key, value]) => (
                        <span key={key}>{key}: {value}</span>
                      ))}
                    </p>
                  )}
                  <p className={styles.price}>{item.price} ₽</p>
                </div>

                <div className={styles.itemActions}>
                  <div className={styles.quantity}>
                    <button
                      onClick={() => handleQuantityChange(item.id, item.quantity - 1)}
                      disabled={loading}
                    >
                      -
                    </button>
                    <span>{item.quantity}</span>
                    <button
                      onClick={() => handleQuantityChange(item.id, item.quantity + 1)}
                      disabled={loading}
                    >
                      +
                    </button>
                  </div>

                  <button
                    onClick={() => handleRemoveItem(item.id)}
                    className={styles.removeButton}
                    disabled={loading}
                  >
                    Удалить
                  </button>
                </div>

                <div className={styles.itemTotal}>
                  {item.total_price} ₽
                </div>
              </div>
            ))}
          </div>

          <div className={styles.summary}>
            <h2>Итого</h2>
            <div className={styles.summaryRow}>
              <span>Товаров:</span>
              <span>{summary.total_items}</span>
            </div>
            <div className={styles.summaryRow}>
              <span>Сумма:</span>
              <span className={styles.totalPrice}>{summary.total_price} ₽</span>
            </div>
            <button className={styles.checkoutButton}>
              Оформить заказ
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default Cart;
