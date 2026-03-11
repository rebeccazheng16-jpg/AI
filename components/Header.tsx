'use client';

import { useLanguage } from '@/contexts/LanguageContext';
import Image from 'next/image';
import { useState, useEffect } from 'react';

export function Header() {
  const { language, setLanguage, t } = useLanguage();
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
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
    <header
      className={`fixed top-0 left-0 right-0 z-50 bg-white border-b transition-all duration-300 ${
        isScrolled ? 'border-gray-200 shadow-sm' : 'border-[#E5E7EB]'
      }`}
    >
      <div className="max-w-[1400px] mx-auto px-8 h-20 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-[#1A1A1A] rounded flex items-center justify-center text-white font-light text-lg">
            S
          </div>
          <span className="text-[#1A1A1A] font-light text-lg tracking-tight">
            Star Metro Management
          </span>
        </div>

        <nav className="hidden md:flex items-center gap-8">
          <button
            onClick={() => scrollToSection('models')}
            className="text-[#1A1A1A] font-light text-sm hover:text-[#6B7280] transition-colors duration-300"
          >
            {t('Models', '模特')}
          </button>
          <button
            onClick={() => scrollToSection('process')}
            className="text-[#1A1A1A] font-light text-sm hover:text-[#6B7280] transition-colors duration-300"
          >
            {t('Process', '工作流程')}
          </button>
          <button
            onClick={() => scrollToSection('case-study')}
            className="text-[#1A1A1A] font-light text-sm hover:text-[#6B7280] transition-colors duration-300"
          >
            {t('Case Study', '案例研究')}
          </button>
          <button
            onClick={() => scrollToSection('markets')}
            className="text-[#1A1A1A] font-light text-sm hover:text-[#6B7280] transition-colors duration-300"
          >
            {t('Markets', '市场')}
          </button>
        </nav>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setLanguage('en')}
            className={`px-3 py-1.5 text-sm font-light transition-all duration-300 ${
              language === 'en'
                ? 'text-[#1A1A1A] font-normal'
                : 'text-[#6B7280] hover:text-[#1A1A1A]'
            }`}
          >
            EN
          </button>
          <span className="text-[#E5E7EB]">|</span>
          <button
            onClick={() => setLanguage('zh')}
            className={`px-3 py-1.5 text-sm font-light transition-all duration-300 ${
              language === 'zh'
                ? 'text-[#1A1A1A] font-normal'
                : 'text-[#6B7280] hover:text-[#1A1A1A]'
            }`}
          >
            中文
          </button>
        </div>
      </div>
    </header>
  );
}
