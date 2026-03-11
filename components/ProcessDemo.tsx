'use client';

import { useLanguage } from '@/contexts/LanguageContext';
import { motion } from 'framer-motion';
import { Play, Video } from 'lucide-react';
import { useRef, useState } from 'react';

const sceneData = [
  { id: 'S1', sceneEn: 'Looking at phone → looks up', sceneZh: '看手机→抬头', dialogue: '"Guys, udah 5 orang tanya aku pakai apa..."' },
  { id: 'S2', sceneEn: 'Shrugs, hesitates to speak', sceneZh: '耸肩欲言又止', dialogue: '"Sebenernya nggak mau bilang, tapi..."' },
  { id: 'S3', sceneEn: 'Takes product from bag', sceneZh: '从包掏出产品', dialogue: '"Ini dia rahasianya — masker dari Veirfoo"' },
  { id: 'S4', sceneEn: 'Applies milky gel', sceneZh: '涂乳白色凝胶', dialogue: '"Aku pakai ini tiap malam, 15 menit sebelum tidur"' },
  { id: 'S5', sceneEn: 'Mask sets, scrolls phone', sceneZh: '成膜后刷手机', dialogue: '"Dan rasanya kayak jelly dingin gitu di muka..."' },
  { id: 'S6', sceneEn: 'Morning glow, bare skin', sceneZh: '晨光素颜水润', dialogue: '"Besok paginya, muka aku..."' },
  { id: 'S7', sceneEn: 'Holds product, whispers', sceneZh: '手持产品悄悄话', dialogue: '"Serius deh, ini beneran ngebantu..."' },
  { id: 'S8', sceneEn: 'Looks down → holds up silver tube', sceneZh: '低头→举起银管', dialogue: '"Ada DNA, kolagen, aman, dan nggak mahal"' },
  { id: 'S9', sceneEn: 'Points to camera, CTA', sceneZh: '指向镜头 CTA', dialogue: '"Kalau mau tau lebih, link di bio ya!"' },
];

export function ProcessDemo() {
  const { t, language } = useLanguage();
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  return (
    <section id="process" className="bg-white py-32">
      <div className="max-w-[1400px] mx-auto px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <h2 className="text-5xl font-light text-[#1A1A1A] mb-4">
            {t('See the Pipeline in Action', '实际工作流程')}
          </h2>
          <p className="text-lg text-[#6B7280] font-light">
            {t(
              'A real production case — VEIRFOO × Kirana × Indonesia',
              '真实案例演示 — 薇尔肤 × Kirana × 印尼市场'
            )}
          </p>
        </motion.div>

        <div className="relative">
          <div className="absolute left-8 top-0 bottom-0 w-px bg-[#E5E7EB]" />

          <div className="space-y-16">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="relative pl-20"
            >
              <div className="absolute left-[1.6rem] top-0 w-3 h-3 rounded-full bg-[#1A1A1A]" />
              <div className="text-xs text-[#6B7280] font-light mb-4 tracking-wider">
                01 / {t('Brief', '简报')}
              </div>
              <h3 className="text-3xl font-light text-[#1A1A1A] mb-8">
                {t('Product + Creator', '产品简报 + 创作者选择')}
              </h3>
              <div className="grid md:grid-cols-2 gap-8">
                <div className="bg-white border border-[#E5E7EB] rounded-lg p-8 flex flex-col items-center justify-center">
                  <div className="h-64 w-full rounded overflow-hidden mb-4">
                    <img src="/veirfoo_product.jpg" alt="VEIRFOO product" className="w-full h-full object-contain" />
                  </div>
                  <p className="text-sm text-[#6B7280] text-center font-light">
                    VEIRFOO · {t('Sodium DNA Water Light Collagen Mask · 65g', 'PDRN 水光胶原面膜 · 65g')}
                  </p>
                </div>
                <div className="bg-white border border-[#E5E7EB] rounded-lg p-8 flex flex-col items-center justify-center">
                  <div className="h-64 w-full rounded overflow-hidden mb-4">
                    <img src="/models/kirana_front.jpg" alt="Kirana" className="w-full h-full object-cover object-top" />
                  </div>
                  <div className="text-center space-y-1">
                    <p className="text-sm text-[#1A1A1A] font-light">Kirana × 🇮🇩 Indonesia</p>
                    <p className="text-xs text-[#6B7280] font-light">
                      {t('Luxury lifestyle · Muslim-friendly · Bahasa Indonesia', '奢华生活方式 · 穆斯林友好 · 印尼语')}
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="relative pl-20"
            >
              <div className="absolute left-[1.6rem] top-0 w-3 h-3 rounded-full bg-[#1A1A1A]" />
              <div className="text-xs text-[#6B7280] font-light mb-4 tracking-wider">
                02 / {t('Script', '脚本')}
              </div>
              <h3 className="text-3xl font-light text-[#1A1A1A] mb-4">
                {t('Template 3 — "Best Friend Recommendation"', '脚本模板 3 ——「闺蜜安利型」')}
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
                {sceneData.map((scene) => (
                  <div
                    key={scene.id}
                    className="bg-white border border-[#E5E7EB] rounded-lg p-6 hover:border-[#1A1A1A] transition-colors duration-300"
                  >
                    <div className="text-xs text-[#6B7280] font-light mb-3">{scene.id}</div>
                    <div className="text-sm text-[#1A1A1A] mb-2 font-light">{language === 'en' ? scene.sceneEn : scene.sceneZh}</div>
                    <div className="text-xs text-[#6B7280] italic">{scene.dialogue}</div>
                  </div>
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="relative pl-20"
            >
              <div className="absolute left-[1.6rem] top-0 w-3 h-3 rounded-full bg-[#1A1A1A]" />
              <div className="text-xs text-[#6B7280] font-light mb-4 tracking-wider">
                03 / {t('Keyframes', '关键帧')}
              </div>
              <h3 className="text-3xl font-light text-[#1A1A1A] mb-2">
                {t('AI-Generated First & Last Frames', 'AI 生成首尾帧')}
              </h3>
              <p className="text-sm text-[#6B7280] font-light mb-8">
                {t('18 keyframes · 9 segment pairs · Generated by Gemini', '18 张 · 9 对 · Gemini 生成')}
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {sceneData.map((scene) => (
                  <div key={scene.id} className="space-y-3">
                    <div className="flex items-center gap-2">
                      <div className="aspect-[9/16] w-full rounded overflow-hidden border border-[#E5E7EB]">
                        <img src={`/frames/${scene.id}_first.png`} alt={`${scene.id} first frame`} className="w-full h-full object-cover" />
                      </div>
                      <span className="text-[#6B7280] flex-shrink-0">→</span>
                      <div className="aspect-[9/16] w-full rounded overflow-hidden border border-[#E5E7EB]">
                        <img src={`/frames/${scene.id}_last.png`} alt={`${scene.id} last frame`} className="w-full h-full object-cover" />
                      </div>
                    </div>
                    <div className="text-xs text-[#6B7280] text-center font-light">{scene.id} · {language === 'en' ? scene.sceneEn : scene.sceneZh}</div>
                  </div>
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="relative pl-20"
            >
              <div className="absolute left-[1.6rem] top-0 w-3 h-3 rounded-full bg-green-500" />
              <div className="text-xs text-[#6B7280] font-light mb-4 tracking-wider">
                04 / {t('Final Video', '成片')}
              </div>
              <h3 className="text-3xl font-light text-[#1A1A1A] mb-2">
                {t('Final Cut · Kirana × VEIRFOO', '成片 · Kirana × 薇尔肤')}
              </h3>
              <p className="text-sm text-[#6B7280] font-light mb-8">
                {t('9 clips · 60s · Powered by Veo 3.1', '9 段剪辑 · 60秒 · Veo 3.1 生成')}
              </p>
              <div
                className="relative w-full max-w-sm mx-auto aspect-[9/16] rounded-xl overflow-hidden bg-black group cursor-pointer"
                onClick={togglePlay}
              >
                <video
                  ref={videoRef}
                  src="/videos/kirana_final.mp4"
                  className="w-full h-full object-cover"
                  onEnded={() => setIsPlaying(false)}
                  playsInline
                />
                {!isPlaying && (
                  <div className="absolute inset-0 flex items-center justify-center bg-black/20 group-hover:bg-black/30 transition-all duration-300">
                    <div className="w-16 h-16 rounded-full bg-white/90 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                      <Play className="w-7 h-7 text-[#1A1A1A] ml-1" fill="currentColor" />
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
}
