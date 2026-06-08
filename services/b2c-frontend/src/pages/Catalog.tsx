import { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { productsApi, categoriesApi } from '../api';
import type { Product, Category, SKUShort } from '../types/api';
import styles from './Catalog.module.css';

interface ProductWithSku extends Product {
  skuData?: SKUShort;
}

interface CategoryWithLevel extends Category {
  level: number;
  hasChildren?: boolean;
}

const Catalog = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [products, setProducts] = useState<ProductWithSku[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());

  const categoryId = searchParams.get('category');
  const page = parseInt(searchParams.get('page') || '1', 10);
  const limit = 20;

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const data = await categoriesApi.getCategoriesTree();
        console.log('Categories response:', data);
        setCategories(data.items || []);
        
        // Expand "Все товары" category by default
        if (data.items && data.items.length > 0) {
          const rootCategory = data.items[0];
          if (rootCategory.name === 'Все товары') {
            setExpandedCategories(new Set([rootCategory.id]));
          }
        }
      } catch (err) {
        console.error('Failed to fetch categories:', err);
      }
    };
    fetchCategories();
  }, []);

  useEffect(() => {
    const fetchProducts = async () => {
      if (!categoryId) {
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const data = await productsApi.getProductsList({
          categoryId,
          limit,
          offset: (page - 1) * limit,
          sort: 'default',
          search: '',
        });
        
        // Fetch SKU data for each product
        const productsWithSkus = await Promise.all(
          (data.items || []).map(async (product) => {
            try {
              const skus = await productsApi.getProductSkus(product.id);
              return {
                ...product,
                skuData: skus[0], // Get first SKU
              };
            } catch (err) {
              console.error(`Failed to fetch SKUs for product ${product.id}:`, err);
              return product;
            }
          })
        );
        
        setProducts(productsWithSkus);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, [categoryId, page]);

  const handleCategorySelect = (catId: string) => {
    setSearchParams({ category: catId, page: '1' });
  };

  const toggleCategory = (catId: string) => {
    setExpandedCategories((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(catId)) {
        newSet.delete(catId);
      } else {
        newSet.add(catId);
      }
      return newSet;
    });
  };

  // Flatten category tree to display visible categories only
  const flattenCategories = (cats: Category[]): CategoryWithLevel[] => {
    const result: CategoryWithLevel[] = [];
    const flatten = (items: Category[], level = 0) => {
      items.forEach((cat) => {
        const hasChildren = cat.children && cat.children.length > 0;
        result.push({ ...cat, level, hasChildren });
        // Only show children if parent is expanded
        if (hasChildren && expandedCategories.has(cat.id)) {
          flatten(cat.children, level + 1);
        }
      });
    };
    flatten(cats);
    return result;
  };

  const flatCategories = flattenCategories(categories);

  if (loading && categories.length === 0) {
    return <div className={styles.loading}>Загрузка...</div>;
  }

  return (
    <div className={styles.catalog}>
      <h1>Каталог товаров</h1>

      <div className={styles.content}>
        <aside className={styles.sidebar}>
          <h2>Категории</h2>
          <ul className={styles.categoryList}>
            {flatCategories.map((category) => (
              <li key={category.id} style={{ marginLeft: `${category.level * 1.5}rem` }}>
                <div className={styles.categoryItem}>
                  {category.hasChildren && (
                    <button
                      className={styles.expandButton}
                      onClick={() => toggleCategory(category.id)}
                      aria-label={expandedCategories.has(category.id) ? 'Свернуть' : 'Развернуть'}
                    >
                      {expandedCategories.has(category.id) ? '▼' : '▶'}
                    </button>
                  )}
                  <button
                    className={`${styles.categoryButton} ${categoryId === category.id ? styles.active : ''}`}
                    onClick={() => handleCategorySelect(category.id)}
                    style={{ 
                      paddingLeft: category.hasChildren ? '0.5rem' : '2rem'
                    }}
                  >
                    {category.name}
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </aside>

        <main className={styles.products}>
          {!categoryId ? (
            <p className={styles.placeholder}>Выберите категорию для просмотра товаров</p>
          ) : error ? (
            <p className={styles.error}>Ошибка: {error}</p>
          ) : products.length === 0 ? (
            <p className={styles.placeholder}>Товары не найдены</p>
          ) : (
            <div className={styles.productGrid}>
              {products.map((product) => {
                const displayPrice = product.skuData?.price ?? product.price;
                const displayImage = product.skuData?.image?.url || product.image || '/no-image.png';
                
                return (
                  <Link 
                    key={product.id} 
                    to={`/product/${product.id}`} 
                    className={styles.productCard}
                  >
                    <div className={styles.productImage}>
                      <img src={displayImage} alt={product.title} />
                    </div>
                    <div className={styles.productInfo}>
                      <h3>{product.title}</h3>
                      <p className={styles.price}>{displayPrice.toFixed(2)} ₽</p>
                    </div>
                  </Link>
                );
              })}
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default Catalog;
