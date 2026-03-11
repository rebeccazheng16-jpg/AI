'use client';

import { useLanguage } from '@/contexts/LanguageContext';
import { motion } from 'framer-motion';
import { useState } from 'react';

export function ContactCTA() {
  const { t } = useLanguage();
  const [formData, setFormData] = useState({
    brandName: '',
    targetMarket: '',
    email: '',
  });
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    setTimeout(() => {
      setSubmitted(false);
      setFormData({ brandName: '', targetMarket: '', email: '' });
    }, 3000);
  };

  return (
    <section className="bg-white py-32">
      <div className="max-w-[800px] mx-auto px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="text-5xl font-light text-[#1A1A1A] mb-4">
            {t('Want an AI Creator for Your Brand?', '想为你的品牌打造 AI 创作者？')}
          </h2>
          <p className="text-lg text-[#6B7280] font-light">
            {t(
              "We're onboarding select brand partners in Q2 2026.",
              '我们正在筛选 2026 年 Q2 合作品牌，名额有限。'
            )}
          </p>
        </motion.div>

        <motion.form
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.2 }}
          onSubmit={handleSubmit}
          className="space-y-6"
        >
          <div>
            <label className="block text-sm text-[#1A1A1A] mb-2 font-light">
              {t('Brand Name', '品牌名称')}
            </label>
            <input
              type="text"
              required
              value={formData.brandName}
              onChange={(e) => setFormData({ ...formData, brandName: e.target.value })}
              className="w-full px-4 py-3 border border-[#E5E7EB] rounded-sm focus:outline-none focus:border-[#1A1A1A] transition-colors font-light"
            />
          </div>

          <div>
            <label className="block text-sm text-[#1A1A1A] mb-2 font-light">
              {t('Target Market', '目标市场')}
            </label>
            <select
              required
              value={formData.targetMarket}
              onChange={(e) => setFormData({ ...formData, targetMarket: e.target.value })}
              className="w-full px-4 py-3 border border-[#E5E7EB] rounded-sm focus:outline-none focus:border-[#1A1A1A] transition-colors font-light bg-white"
            >
              <option value="">
                {t('Select a market', '选择市场')}
              </option>
              <option value="indonesia">Indonesia</option>
              <option value="japan">Japan</option>
              <option value="korea">Korea</option>
              <option value="vietnam">Vietnam</option>
              <option value="global">Global EN</option>
              <option value="other">{t('Other', '其他')}</option>
            </select>
          </div>

          <div>
            <label className="block text-sm text-[#1A1A1A] mb-2 font-light">
              {t('Contact Email', '联系邮箱')}
            </label>
            <input
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full px-4 py-3 border border-[#E5E7EB] rounded-sm focus:outline-none focus:border-[#1A1A1A] transition-colors font-light"
            />
          </div>

          <button
            type="submit"
            disabled={submitted}
            className="w-full px-8 py-4 bg-[#1A1A1A] text-white text-sm font-light hover:bg-[#2A2A2A] transition-all duration-300 rounded-sm disabled:bg-green-600 disabled:cursor-not-allowed"
          >
            {submitted
              ? t('✓ Application Received', '✓ 已收到申请')
              : t('Apply for Early Access', '申请优先合作')}
          </button>
        </motion.form>
      </div>

      <motion.footer
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="mt-32 text-center space-y-4"
      >
        <div className="flex items-center justify-center gap-3">
          <div className="w-8 h-8 bg-[#1A1A1A] rounded flex items-center justify-center text-white font-light text-sm">
            S
          </div>
          <span className="text-[#6B7280] font-light text-sm">Star Metro Management</span>
        </div>
        <p className="text-xs text-[#6B7280] font-light">
          © 2026 SSM Star Metro Management
        </p>
        <p className="text-xs text-[#6B7280] font-light italic">
          {t(
            'All creators are AI-generated digital personas.',
            '所有创作者均为 AI 生成的数字人物。'
          )}
        </p>
      </motion.footer>
    </section>
  );
}
