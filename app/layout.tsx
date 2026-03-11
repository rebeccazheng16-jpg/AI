import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { LanguageProvider } from '@/contexts/LanguageContext';

const inter = Inter({
  subsets: ['latin'],
  weight: ['200', '300', '400', '500'],
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'SSM Star Metro Management - AI Digital Creator Studio',
  description: 'We build AI-native digital creators for Southeast & East Asia markets',
  openGraph: {
    title: 'SSM Star Metro Management - AI Digital Creator Studio',
    description: 'We build AI-native digital creators for Southeast & East Asia markets',
    images: [
      {
        url: 'https://bolt.new/static/og_default.png',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'SSM Star Metro Management - AI Digital Creator Studio',
    description: 'We build AI-native digital creators for Southeast & East Asia markets',
    images: [
      {
        url: 'https://bolt.new/static/og_default.png',
      },
    ],
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className={inter.className}>
        <LanguageProvider>{children}</LanguageProvider>
      </body>
    </html>
  );
}
