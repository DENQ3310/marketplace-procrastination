import styles from './Home.module.css';

const Home = () => {
  return (
    <div className={styles.home}>
      <section className={styles.hero}>
        <h1>Добро пожаловать в Datak</h1>
        <p>Найдите все, что вам нужно</p>
      </section>
    </div>
  );
};

export default Home;
