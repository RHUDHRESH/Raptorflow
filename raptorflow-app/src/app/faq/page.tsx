'use client';

import { MarketingLayout } from '@/components/marketing/MarketingLayout';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';

const faqCategories = [
  {
    name: 'General',
    questions: [
      {
        question: 'What is RaptorFlow?',
        answer:
          'RaptorFlow is an AI-first marketing operating system that helps founders turn messy business context into clear positioning and a 90-day marketing war plan—then ships weekly Moves that drive revenue.',
      },
      {
        question: 'Who is RaptorFlow for?',
        answer:
          'RaptorFlow is built for founders, small teams, and agency leads who need to grow now without wasting months on unclear positioning and random marketing tactics.',
      },
      {
        question: 'How is RaptorFlow different from other marketing tools?',
        answer:
          'Most tools solve one piece of the puzzle—scheduling, analytics, or content generation. RaptorFlow is a complete system: strategy → execution → tracking → iteration, all connected.',
      },
      {
        question: 'Do I need to be technical to use RaptorFlow?',
        answer:
          'Not at all. RaptorFlow is designed for founders and marketers, not engineers. If you can use email and Google Docs, you can use RaptorFlow.',
      },
    ],
  },
  {
    name: 'Pricing & Billing',
    questions: [
      {
        question: 'Is there a free trial?',
        answer:
          'Yes! All plans include a 14-day free trial. No credit card required to start.',
      },
      {
        question: 'Can I change plans later?',
        answer:
          'Yes, you can upgrade or downgrade at any time. Changes take effect at the start of your next billing cycle.',
      },
      {
        question: 'What payment methods do you accept?',
        answer:
          'We accept all major credit cards (Visa, Mastercard, American Express) and UPI payments for Indian customers.',
      },
      {
        question: 'Do you offer annual billing?',
        answer:
          'Yes! Annual billing saves you 20% compared to monthly billing. Contact us for annual plan options.',
      },
    ],
  },
  {
    name: 'Features',
    questions: [
      {
        question: 'What counts as a "Move"?',
        answer:
          'A Move is a single execution packet—one piece of content with its context, channel, and tracking. It is designed to be completed in one focused session.',
      },
      {
        question: 'What is the difference between Moves and Move Generations?',
        answer:
          'Moves are what you ship. Move Generations are AI-generated options you can choose from. More generations = more options to find the perfect angle.',
      },
      {
        question: 'What is Foundation?',
        answer:
          'Foundation is your strategic base—positioning, messaging, voice, proof points. It is the single source of truth that feeds every campaign and asset.',
      },
      {
        question: 'How does Blackbox work?',
        answer:
          'Blackbox runs A/B tests on your content to prove what works. It suggests experiments, tracks results, and gives you statistically significant insights.',
      },
      {
        question: 'What does Radar track?',
        answer:
          'Radar monitors competitor positioning, messaging, and campaigns. It helps you find positioning gaps and stay ahead of market changes.',
      },
    ],
  },
  {
    name: 'Support',
    questions: [
      {
        question: 'How do I get help if I am stuck?',
        answer:
          'All plans include email support. Glide gets priority response times, and Soar gets dedicated 1:1 support.',
      },
      {
        question: 'Do you offer onboarding help?',
        answer:
          'Yes! Every new account gets a guided onboarding flow. Soar customers get personal onboarding calls with our team.',
      },
      {
        question: 'Is there documentation?',
        answer:
          'Yes, we have comprehensive documentation, video tutorials, and a help center available 24/7.',
      },
    ],
  },
];

export default function FAQPage() {
  return (
    <MarketingLayout>
      {/* Hero */}
      <section className="py-24 lg:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">
              FAQ
            </p>
            <h1 className="font-display text-5xl lg:text-6xl font-medium tracking-tight mb-6">
              Questions? Answers.
            </h1>
            <p className="text-lg lg:text-xl text-muted-foreground leading-relaxed">
              Everything you need to know about RaptorFlow.
            </p>
          </div>
        </div>
      </section>

      {/* FAQ Sections */}
      <section className="pb-24 lg:pb-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-3xl">
            {faqCategories.map((category) => (
              <div key={category.name} className="mb-12">
                <h2 className="font-display text-2xl font-medium mb-6">
                  {category.name}
                </h2>
                <Accordion
                  type="single"
                  collapsible
                  className="w-full space-y-4"
                >
                  {category.questions.map((item, index) => {
                    const key = `${category.name}-${index}`;
                    return (
                      <AccordionItem
                        key={key}
                        value={key}
                        className="rounded-xl border border-border bg-card px-6"
                      >
                        <AccordionTrigger className="text-left font-medium hover:no-underline">
                          {item.question}
                        </AccordionTrigger>
                        <AccordionContent className="text-muted-foreground leading-relaxed pb-6">
                          {item.answer}
                        </AccordionContent>
                      </AccordionItem>
                    );
                  })}
                </Accordion>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Still have questions */}
      <section className="border-t border-border bg-muted/30 py-16">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="font-display text-2xl font-medium mb-4">
              Still have questions?
            </h2>
            <p className="text-muted-foreground mb-6">
              Cannot find the answer you are looking for? Reach out to our team.
            </p>
            <a
              href="mailto:hello@raptorflow.com"
              className="inline-flex items-center text-foreground font-medium hover:underline"
            >
              Contact Support →
            </a>
          </div>
        </div>
      </section>
    </MarketingLayout>
  );
}
