'use client';

import { useLanguage } from '@/contexts/LanguageContext';
import { motion } from 'framer-motion';
import { Play, Plus, X } from 'lucide-react';
import { useRef, useState } from 'react';

const videos = [
  { file: '/videos/yuna_video.mp4', poster: '/models/yuna_front.jpg', labelEn: 'Hand-hold Demo', labelZh: '手持展示' },
  { file: '/videos/yuki_video.mp4', poster: '/models/yuki_front.jpg', labelEn: 'Voiceover Review', labelZh: '口播种草' },
];

export function CaseStudy() {
  const { t } = useLanguage();
  const [modalVideo, setModalVideo] = useState<{ file: string; poster: string; labelEn: string; labelZh: string } | null>(null);

  return (
    <section id="case-study" className="bg-white py-32">
      <div className="max-w-[1400px] mx-auto px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="mb-12"
        >
          <div className="text-xs uppercase tracking-wider text-[#6B7280] font-light mb-6">
            {t('CASE STUDY 01', '案例研究 01')}
          </div>
          <h2 className="text-5xl font-light text-[#1A1A1A] mb-4">
            {t('From Brief to TikTok in 48 Hours', '从简报到 TikTok，48 小时交付')}
          </h2>
          <p className="text-lg text-[#6B7280] font-light">
            Kirana × VEIRFOO × Indonesia
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-12 mb-12">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="space-y-6"
          >
            <div>
              <h3 className="text-sm uppercase tracking-wider text-[#1A1A1A] mb-2 font-light">
                {t('Brand', '品牌')}
              </h3>
              <p className="text-xl text-[#1A1A1A] font-light">VEIRFOO</p>
            </div>
            <div>
              <h3 className="text-sm uppercase tracking-wider text-[#1A1A1A] mb-2 font-light">
                {t('Product', '产品')}
              </h3>
              <p className="text-xl text-[#1A1A1A] font-light">
                {t('PDRN Water Light Collagen Mask · Silver tube · 65g', 'PDRN 水光胶原面膜 · 银色管状 · 65g')}
              </p>
            </div>
            <div>
              <h3 className="text-sm uppercase tracking-wider text-[#1A1A1A] mb-2 font-light">
                {t('Challenge', '挑战')}
              </h3>
              <p className="text-[#6B7280] leading-relaxed font-light">
                {t(
                  'Entering Indonesia market. Local KOC content too costly. Needed authentic, culturally resonant creator content at scale.',
                  '进入印尼市场，本土 KOC 内容成本高昂，需要有文化认同感的大规模创作者内容。'
                )}
              </p>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="space-y-4"
          >
            <div className="grid grid-cols-2 gap-4">
              {videos.map((video, index) => (
                <VideoCard key={index} video={video} onOpen={() => setModalVideo(video)} />
              ))}
            </div>
            <div className="aspect-video rounded-xl border-2 border-dashed border-[#E5E7EB] bg-[#F9FAFB] flex items-center justify-center">
              <div className="text-center">
                <Plus className="w-8 h-8 text-[#6B7280] mx-auto mb-2" strokeWidth={1} />
                <p className="text-sm text-[#6B7280] font-light">
                  {t('More coming soon', '更多视频即将发布')}
                </p>
              </div>
            </div>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="bg-[#111827] text-white py-8 px-12 rounded-lg"
        >
          <div className="flex flex-wrap items-center justify-center gap-8 text-center">
            <div>
              <div className="text-3xl font-light mb-1">9</div>
              <div className="text-sm text-gray-400 font-light">{t('Video Clips', '视频片段')}</div>
            </div>
            <div className="w-px h-12 bg-gray-700" />
            <div>
              <div className="text-3xl font-light mb-1">62</div>
              <div className="text-sm text-gray-400 font-light">{t('Seconds Total', '总秒数')}</div>
            </div>
            <div className="w-px h-12 bg-gray-700" />
            <div>
              <div className="text-3xl font-light mb-1">5</div>
              <div className="text-sm text-gray-400 font-light">{t('Languages Ready', '语言就绪')}</div>
            </div>
            <div className="w-px h-12 bg-gray-700" />
            <div>
              <div className="text-3xl font-light mb-1">1</div>
              <div className="text-sm text-gray-400 font-light">{t('AI Model', 'AI 创作者')}</div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Modal */}
      {modalVideo && (
        <VideoModal video={modalVideo} onClose={() => setModalVideo(null)} />
      )}
    </section>
  );
}

function VideoCard({ video, onOpen }: {
  video: { file: string; poster: string; labelEn: string; labelZh: string };
  onOpen: () => void;
}) {
  const { language } = useLanguage();
  const videoRef = useRef<HTMLVideoElement>(null);

  return (
    <div className="space-y-2">
      <div
        className="relative aspect-[9/16] rounded-xl overflow-hidden bg-[#F9FAFB] border border-[#E5E7EB] group cursor-pointer transition-transform duration-300 hover:scale-105 hover:shadow-lg"
        onClick={onOpen}
        onMouseEnter={() => videoRef.current?.play()}
        onMouseLeave={() => { if (videoRef.current) { videoRef.current.pause(); videoRef.current.currentTime = 0; } }}
      >
        <video
          ref={videoRef}
          src={video.file}
          poster={video.poster}
          className="w-full h-full object-cover"
          muted
          playsInline
          loop
          preload="none"
        />
        <div className="absolute inset-0 flex items-center justify-center bg-black/10 group-hover:bg-black/20 transition-all duration-300">
          <div className="w-12 h-12 rounded-full bg-white/90 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
            <Play className="w-5 h-5 text-[#1A1A1A] ml-1" fill="currentColor" />
          </div>
        </div>
      </div>
      <p className="text-xs text-[#6B7280] font-light text-center">
        {language === 'en' ? video.labelEn : video.labelZh}
      </p>
    </div>
  );
}

function VideoModal({ video, onClose }: {
  video: { file: string; poster: string; labelEn: string; labelZh: string };
  onClose: () => void;
}) {
  const { language } = useLanguage();
  const videoRef = useRef<HTMLVideoElement>(null);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-sm mx-4"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute -top-10 right-0 text-white/70 hover:text-white transition-colors"
        >
          <X className="w-6 h-6" />
        </button>
        <div className="aspect-[9/16] rounded-xl overflow-hidden bg-black">
          <video
            ref={videoRef}
            src={video.file}
            className="w-full h-full object-cover"
            autoPlay
            playsInline
            controls
            preload="none"
          />
        </div>
        <p className="text-center text-white/70 text-sm font-light mt-3">
          {language === 'en' ? video.labelEn : video.labelZh}
        </p>
      </div>
    </div>
  );
}
