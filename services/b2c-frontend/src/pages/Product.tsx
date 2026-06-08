import { useParams } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { productsApi } from '../api';
import useCartStore from '../store/cartStore';
import type { ProductDetail, SKUDetail } from '../types/api';
import styles from './Product.module.css';

const Product = () => {
  const { id } = useParams<{ id: string }>();
  const [product, setProduct] = useState<ProductDetail | null>(null);
  const [selectedSku, setSelectedSku] = useState<SKUDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [addingToCart, setAddingToCart] = useState(false);

  const addItem = useCartStore((state) => state.addItem);

  useEffect(() => {
    const fetchProduct = async () => {
      if (!id) return;

      setLoading(true);
      setError(null);

      try {
        const productData = await productsApi.getProductById(id);
        setProduct(productData);
        
        // Select first SKU by default
        if (productData.skus && productData.skus.length > 0) {
          setSelectedSku(productData.skus[0]);
        }
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
  }, [id]);

  const handleAddToCart = async () => {
    if (!selectedSku) return;

    setAddingToCart(true);
    try {
      await addItem(selectedSku.id, 1);
      alert('Товар добавлен в корзину');
    } catch (err) {
      alert('Ошибка при добавлении в корзину: ' + (err as Error).message);
    } finally {
      setAddingToCart(false);
    }
  };

  if (loading) {
    return <div className={styles.loading}>Загрузка...</div>;
  }

  if (error) {
    return <div className={styles.error}>Ошибка: {error}</div>;
  }

  if (!product) {
    return <div className={styles.error}>Товар не найден</div>;
  }

  const displayImage = selectedSku?.images?.[0]?.url || product.images?.[0]?.url || '/no-image.png';

  return (
    <div className={styles.product}>
      <div className={styles.content}>
        <div className={styles.imageSection}>
          <div className={styles.mainImage}>
            <img src={displayImage} alt={product.title} />
          </div>
        </div>

        <div className={styles.info}>
          <h1>{product.title}</h1>
          
          {product.description && (
            <p className={styles.description}>{product.description}</p>
          )}

          {product.skus && product.skus.length > 0 && (
            <div className={styles.skuSection}>
              <h3>Варианты:</h3>
              <div className={styles.skuList}>
                {product.skus.map((sku) => (
                  <button
                    key={sku.id}
                    className={`${styles.skuButton} ${selectedSku?.id === sku.id ? styles.selected : ''}`}
                    onClick={() => setSelectedSku(sku)}
                  >
                    {sku.name}
                  </button>
                ))}
              </div>
            </div>
          )}

          {selectedSku && (
            <div className={styles.priceSection}>
              <p className={styles.price}>{selectedSku.price.toFixed(2)} ₽</p>
              <p className={styles.stock}>В наличии: {selectedSku.active_quantity} шт.</p>
              <button
                className={styles.addToCartButton}
                onClick={handleAddToCart}
                disabled={addingToCart || selectedSku.active_quantity === 0}
              >
                {addingToCart ? 'Добавление...' : selectedSku.active_quantity > 0 ? 'Добавить в корзину' : 'Нет в наличии'}
              </button>
            </div>
          )}

          {product.characteristics && product.characteristics.length > 0 && (
            <div className={styles.characteristicsSection}>
              <h3>Характеристики:</h3>
              <dl className={styles.characteristicsList}>
                {product.characteristics.map((char) => (
                  <div key={char.id} className={styles.characteristicItem}>
                    <dt>{char.name}</dt>
                    <dd>{char.value}</dd>
                  </div>
                ))}
              </dl>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Product;
