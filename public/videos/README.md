# Video Assets

Place video files in this directory:

## Case Study Videos
Add or reorder videos by editing the `videos` array in `/components/CaseStudy.tsx`

Example videos:
- yuna_video.mp4 (Hand-hold Demo / 手持展示)
- yuki_video.mp4 (Voiceover Review / 口播种草)

To add more videos, update the array:
```typescript
const videos = [
  { file: '/videos/yuna_video.mp4', labelEn: 'Hand-hold Demo', labelZh: '手持展示' },
  { file: '/videos/yuki_video.mp4', labelEn: 'Voiceover Review', labelZh: '口播种草' },
  // ADD NEW VIDEOS HERE:
  // { file: '/videos/new_video.mp4', labelEn: 'English Label', labelZh: '中文标签' },
];
```
