'use client';

import { useLanguage } from '@/contexts/LanguageContext';
import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';

export function HowItWorks() {
  const { t } = useLanguage();

  const steps = [
    {
      number: '01',
      titleEn: 'Model Identity',
      titleZh: '创作者建模',
      descEn:
        'From a reference photo, we build a permanent AI creator — consistent face, style, and persona across all content.',
      descZh: '从参考照片建立永久 AI 创作者档案，保持跨内容一致的外形与人设。',
    },
    {
      number: '02',
      titleEn: 'AI Video Generation',
      titleZh: 'AI 视频生成',
      descEn:
        'A text brief becomes a full storyboard. Videos generated clip by clip using Veo 3.1, Gemini, and Seedream 2.0.',
      descZh: '文字简报生成完整分镜脚本，由 Veo 3.1、Gemini 及即梦 2.0 逐段生成视频。',
    },
    {
      number: '03',
      titleEn: 'Multi-Market Output',
      titleZh: '多市场输出',
      descEn:
        'Each video adapted for its market — language, pacing, platform format. Upload-ready for TikTok.',
      descZh: '每条视频针对目标市场本地化——语言、节奏、平台格式，可直接上传 TikTok。',
    },
  ];

  return (
    <section className="bg-white py-32">
      <div className="max-w-[1400px] mx-auto px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <h2 className="text-5xl font-light text-[#1A1A1A] mb-4">
            {t('Three Steps. Any Brand. Any Market.', '三步完成，覆盖任意品牌与市场')}
          </h2>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8">
          {steps.map((step, index) => (
            <motion.div
              key={step.number}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className="relative"
            >
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-8 -right-4 z-10">
                  <ArrowRight className="w-6 h-6 text-[#E5E7EB]" strokeWidth={1} />
                </div>
              )}
              <div className="bg-white border border-[#E5E7EB] rounded-lg p-8 h-full hover:border-[#1A1A1A] transition-all duration-300">
                <div className="text-xs text-[#6B7280] font-light mb-6 tracking-wider">
                  {step.number}
                </div>
                <h3 className="text-2xl font-light text-[#1A1A1A] mb-4">
                  {t(step.titleEn, step.titleZh)}
                </h3>
                <p className="text-[#6B7280] leading-relaxed font-light">
                  {t(step.descEn, step.descZh)}
                </p>
              </div>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="text-center mt-12 text-sm text-[#6B7280] font-light"
        >
          {t('Powered by Gemini · Veo 3.1 · Seedream 2.0', '技术支持：Gemini · Veo 3.1 · 即梦 2.0')}
        </motion.div>
      </div>
    </section>
  );
}
