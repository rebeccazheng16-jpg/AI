import { Header } from '@/components/Header';
import { HeroSection } from '@/components/HeroSection';
import { ModelGallery } from '@/components/ModelGallery';
import { ProcessDemo } from '@/components/ProcessDemo';
import { CaseStudy } from '@/components/CaseStudy';
import { HowItWorks } from '@/components/HowItWorks';
import { Markets } from '@/components/Markets';
import { ContactCTA } from '@/components/ContactCTA';

export default function Home() {
  return (
    <div className="min-h-screen bg-white">
      <Header />
      <main>
        <HeroSection />
        <ModelGallery />
        <ProcessDemo />
        <CaseStudy />
        <HowItWorks />
        <Markets />
        <ContactCTA />
      </main>
    </div>
  );
}
