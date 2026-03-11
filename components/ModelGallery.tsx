'use client';

import { useLanguage } from '@/contexts/LanguageContext';
import { motion } from 'framer-motion';
import { useState } from 'react';

interface Model {
  name: string;
  flag: string;
  country: string;
  language: string;
  positioning: { en: string; zh: string };
  status: 'live' | 'coming';
  portraitImage: string;
  turnaroundImage: string;
}

const models: Model[] = [
  {
    name: 'Kirana',
    flag: '🇮🇩',
    country: 'Indonesia',
    language: 'Bahasa Indonesia',
    positioning: {
      en: 'Luxury lifestyle · Muslim-friendly',
      zh: '奢华生活方式 · 穆斯林友好',
    },
    status: 'live',
    portraitImage: '/models/kirana_front.jpg',
    turnaroundImage: '/models/kirana_turnaround.jpg',
  },
  {
    name: 'Yuki',
    flag: '🇯🇵',
    country: 'Japan',
    language: '日本語',
    positioning: {
      en: 'J-aesthetic · Knowledge creator',
      zh: '日式美学 · 知识创作者',
    },
    status: 'live',
    portraitImage: '/models/yuki_front.jpg',
    turnaroundImage: '/models/yuki_turnaround.jpg',
  },
  {
    name: 'Yuna',
    flag: '🇰🇷',
    country: 'Korea',
    language: '한국어',
    positioning: {
      en: 'K-beauty · Gen Z energy',
      zh: 'K-beauty · Z世代活力',
    },
    status: 'live',
    portraitImage: '/models/yuna_front.jpg',
    turnaroundImage: '/models/yuna_turnaround.jpg',
  },
  {
    name: 'Hoa',
    flag: '🇻🇳',
    country: 'Vietnam',
    language: 'Tiếng Việt',
    positioning: {
      en: 'Fresh · Sunshine lifestyle',
      zh: '清新 · 阳光生活方式',
    },
    status: 'coming',
    portraitImage: '/models/hoa_front.jpg',
    turnaroundImage: '/models/hoa_turnaround.jpg',
  },
  {
    name: 'Lily',
    flag: '🌏',
    country: 'Global',
    language: 'English',
    positioning: {
      en: 'Mixed · Z-gen vitality',
      zh: '混血 · Z世代活力',
    },
    status: 'coming',
    portraitImage: '/models/lily_front.jpg',
    turnaroundImage: '/models/lily_turnaround.jpg',
  },
];

export function ModelGallery() {
  const { t, language } = useLanguage();
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  return (
    <section id="models" className="bg-white py-24">
      <div className="max-w-[1400px] mx-auto px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="space-y-0"
        >
          {models.map((model, index) => (
            <div
              key={model.name}
              className="relative border-b border-[#E5E7EB] overflow-hidden"
              style={{ height: '280px' }}
              onMouseEnter={() => setHoveredIndex(index)}
              onMouseLeave={() => setHoveredIndex(null)}
            >
              <div className="flex h-full">
                <div
                  className="relative bg-[#F9FAFB] transition-all duration-400 ease-out overflow-hidden"
                  style={{
                    width: hoveredIndex === index ? '60%' : '28%',
                  }}
                >
                  <img
                    src={hoveredIndex === index ? model.turnaroundImage : model.portraitImage}
                    alt={model.name}
                    className={`w-full h-full ${hoveredIndex === index ? 'object-contain' : 'object-cover object-top'}`}
                  />
                </div>

                <div
                  className="flex-1 py-8 px-12 transition-all duration-400 ease-out flex flex-col justify-center"
                  style={{
                    width: hoveredIndex === index ? '40%' : '72%',
                  }}
                >
                  {hoveredIndex === index ? (
                    <div className="space-y-3">
                      <h3 className="text-3xl font-light text-[#1A1A1A]">
                        {model.name}
                      </h3>
                      <div className="flex items-center gap-2">
                        <div
                          className={`w-2 h-2 rounded-full ${
                            model.status === 'live' ? 'bg-green-500' : 'bg-gray-300'
                          }`}
                        />
                        <span className="text-sm text-[#6B7280] font-light">
                          {model.status === 'live'
                            ? t('Live', '上线')
                            : t('Coming Soon', '即将推出')}
                        </span>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <h3 className="text-5xl font-light text-[#1A1A1A] tracking-tight">
                        {model.name}
                      </h3>
                      <div className="flex items-center gap-3 text-sm text-[#6B7280] font-light">
                        <span className="text-2xl">{model.flag}</span>
                        <span>{model.country}</span>
                        <span>·</span>
                        <span>{model.language}</span>
                      </div>
                      <p className="text-[#6B7280] italic font-light">
                        {language === 'en'
                          ? model.positioning.en
                          : model.positioning.zh}
                      </p>
                      <div className="flex items-center gap-2">
                        <div
                          className={`w-2 h-2 rounded-full ${
                            model.status === 'live' ? 'bg-green-500' : 'bg-gray-300'
                          }`}
                        />
                        <span className="text-sm text-[#6B7280] font-light">
                          {model.status === 'live'
                            ? t('Live', '上线')
                            : t('Coming Soon', '即将推出')}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
