'use client';

import { useLanguage } from '@/contexts/LanguageContext';
import { motion } from 'framer-motion';

const markets = [
  { flag: '🇮🇩', country: 'Indonesia', creator: 'Kirana', language: 'Bahasa Indonesia' },
  { flag: '🇯🇵', country: 'Japan', creator: 'Yuki', language: '日本語' },
  { flag: '🇰🇷', country: 'Korea', creator: 'Yuna', language: '한국어' },
  { flag: '🇻🇳', country: 'Vietnam', creator: 'Hoa', language: 'Tiếng Việt' },
  { flag: '🌏', country: 'Global EN', creator: 'Lily', language: 'English' },
];

export function Markets() {
  const { t } = useLanguage();

  return (
    <section id="markets" className="bg-white py-32">
      <div className="max-w-[1400px] mx-auto px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <h2 className="text-5xl font-light text-[#1A1A1A] mb-4">
            {t('Five Creators. Five Markets.', '五位创作者，五大市场')}
          </h2>
          <p className="text-lg text-[#6B7280] font-light">
            {t(
              'One production pipeline. Localized for every market.',
              '统一生产流程，每个市场独立本地化。'
            )}
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
          {markets.map((market, index) => (
            <motion.div
              key={market.country}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.05 }}
              className="bg-white border border-[#E5E7EB] rounded-lg p-8 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 cursor-pointer"
            >
              <div className="text-center space-y-4">
                <div className="text-5xl mb-6">{market.flag}</div>
                <div className="space-y-2">
                  <h3 className="text-xl font-light text-[#1A1A1A]">{market.country}</h3>
                  <p className="text-sm text-[#6B7280] font-light">{market.creator}</p>
                  <p className="text-xs text-[#6B7280] font-light">{market.language}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
