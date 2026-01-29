// components/InfiniteCarousel.jsx
import { Swiper, SwiperSlide } from 'swiper/react';
import { Autoplay } from 'swiper/modules';
import 'swiper/css';
import styles from '@/styles/InfiniteCarousel.module.css'

const InfiniteCarousel = ({ images }) => {
  return (
    <Swiper
      modules={[Autoplay]}
      spaceBetween={20}
      loop={true}
      autoplay={{ 
        delay: 3000, 
        disableOnInteraction: false 
      }}
      // slidesPerView={1.2}
      // centeredSlides={true}
      className={styles.swiper}      
    >
      {images.map((image, index) => (
        <SwiperSlide key={`${image.id}-${index}`} className={styles.slide}>
          <img src={image.url} alt='' loading="lazy" className={styles.carousel} />
        </SwiperSlide>
      ))}
    </Swiper>
  );
};

export default InfiniteCarousel;