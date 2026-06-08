import { Link } from 'react-router-dom';
import useCartStore from '../../store/cartStore';
import useThemeStore from '../../store/themeStore';
import styles from './Header.module.css';

const Header = () => {
  const itemCount = useCartStore((state) => state.getItemCount());
  const { theme, toggleTheme } = useThemeStore();

  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <Link to="/" className={styles.logo}>
          <h1>Datak</h1>
        </Link>
        
        <nav className={styles.nav}>
          <Link to="/" className={styles.navLink}>Главная</Link>
          <Link to="/catalog" className={styles.navLink}>Каталог</Link>
          <Link to="/cart" className={styles.navLink}>
            Корзина
            {itemCount > 0 && (
              <span className={styles.badge}>{itemCount}</span>
            )}
          </Link>
          <button 
            onClick={toggleTheme} 
            className={styles.themeToggle}
            aria-label="Переключить тему"
          >
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
        </nav>
      </div>
    </header>
  );
};

export default Header;
