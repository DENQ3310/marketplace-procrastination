import styles from './Footer.module.css';

const Footer = () => {
  return (
    <footer className={styles.footer}>
      <div className={styles.container}>
        <p>
          &copy; 2026 Datak. Frontend vibecoded by{' '}
          <a 
            href="https://github.com/veraven21" 
            target="_blank" 
            rel="noopener noreferrer"
            className={styles.link}
          >
            VeRaven
          </a>
        </p>
        <p>
          <a 
            href="https://github.com/saneczkab/marketplace-datak" 
            target="_blank" 
            rel="noopener noreferrer"
            className={styles.link}
          >
            Source code
          </a>
        </p>
      </div>
    </footer>
  );
};

export default Footer;
