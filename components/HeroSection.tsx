'use client';

import { useLanguage } from '@/contexts/LanguageContext';
import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

const modelImages = [
  '/models/kirana_front.jpg',
  '/models/yuki_front.jpg',
  '/models/yuna_front.jpg',
  '/models/hoa_front.jpg',
  '/models/lily_front.jpg',
];

export function HeroSection() {
  const { t } = useLanguage();
  const [scrollPosition, setScrollPosition] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setScrollPosition((prev) => (prev + 0.2) % 500);
    }, 50);
    return () => clearInterval(interval);
  }, []);

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      const headerHeight = 80;
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - headerHeight;

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });
    }
  };

  return (
    <section className="h-screen min-h-[600px] bg-white pt-20 flex items-center">
      <div className="max-w-[1400px] mx-auto px-8 w-full flex items-center gap-12">
        <motion.div
          className="w-[55%] space-y-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <div className="text-xs uppercase tracking-wider text-[#6B7280] font-light">
            {t('AI DIGITAL CREATOR STUDIO', 'AI 数字创作者工作室')}
          </div>

          <h1 className="text-7xl font-light text-[#1A1A1A] leading-tight tracking-tight">
            {t('One Brand. One Click.', '一个品牌，一键出海')}
          </h1>

          <p className="text-lg text-[#6B7280] leading-relaxed font-light max-w-xl">
            {t(
              'We build AI-native digital creators for Southeast & East Asia — each fluent in her language, her culture, her market.',
              '我们为东南亚与东亚市场打造 AI 原生数字创作者——每一位都精通她的语言、她的文化、她的市场。'
            )}
          </p>

          <div className="flex gap-4 pt-4">
            <button
              onClick={() => scrollToSection('models')}
              className="px-8 py-3.5 bg-[#1A1A1A] text-white text-sm font-light hover:bg-[#2A2A2A] transition-all duration-300 rounded-sm"
            >
              {t('See Our Models', '查看模特')}
            </button>
            <button
              onClick={() => scrollToSection('process')}
              className="px-8 py-3.5 border border-[#E5E7EB] text-[#1A1A1A] text-sm font-light hover:border-[#1A1A1A] transition-all duration-300 rounded-sm"
            >
              {t('See the Process', '查看工作流程')}
            </button>
          </div>
        </motion.div>

        <motion.div
          className="w-[45%] h-[80vh] relative overflow-hidden"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 0.3 }}
        >
          <div
            className="absolute inset-0 flex flex-col gap-6"
            style={{
              transform: `translateY(-${scrollPosition}px)`,
            }}
          >
            {[...modelImages, ...modelImages].map((img, idx) => (
              <div
                key={idx}
                className="h-[300px] bg-[#F9FAFB] rounded flex items-center justify-center relative overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-b from-transparent to-[#1A1A1A]/10" />
                <div className="text-[#6B7280] text-sm">
                  {t('Model Image', '模特图片')} {(idx % 5) + 1}
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
