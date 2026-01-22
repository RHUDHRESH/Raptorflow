# ≡ƒÜÇ RaptorFlow - Marketing Operating System

> **The complete marketing operating system for founders and marketing teams**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Next.js](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4-38B2AC)](https://tailwindcss.com/)

## ≡ƒÄ» Overview

RaptorFlow is a comprehensive marketing operating system designed specifically for founders and marketing teams. It provides everything you need to manage your entire marketing workflow - from strategic foundation to AI-powered content generation, campaign management, and advanced analytics.

### Γ£¿ Key Features

- ≡ƒÅù∩╕Å **Marketing Foundation** - Build your strategic marketing pillars
- ≡ƒæÑ **Customer Cohorts** - Manage and analyze customer segments
- ΓÜí **Marketing Moves** - Track weekly marketing execution
- ≡ƒôó **Campaign Management** - Run multi-channel marketing campaigns
- ≡ƒñû **AI Content Generation** - Create marketing content with AI
- ≡ƒôè **Advanced Analytics** - Get insights and predictive analytics
- ≡ƒöö **Real-time Notifications** - Stay updated with live alerts
- ΓÜÖ∩╕Å **Comprehensive Settings** - Customize your experience
- ≡ƒôÜ **Help Center** - Get support and learn best practices

## ≡ƒÜÇ Quick Start

### Prerequisites
- Node.js 18+
- npm or yarn
- Modern web browser

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-org/raptorflow.git
cd raptorflow/frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Set up environment variables**
```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

4. **Run the development server**
```bash
npm run dev
```

5. **Open your browser**
Navigate to [http://localhost:3000](http://localhost:3000)

## ≡ƒÅù∩╕Å Architecture

### Frontend Stack
- **Next.js 16** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS v4** - Utility-first CSS framework
- **Framer Motion** - Smooth animations
- **Zustand** - State management
- **Shadcn/ui** - Component library

### Backend Integration
- **FastAPI** - Python web framework
- **Type-safe API client** - With mock data fallback
- **Real-time updates** - WebSocket connections
- **Error handling** - Graceful degradation

## ≡ƒô▒ Features Deep Dive

### ≡ƒÅù∩╕Å Marketing Foundation
Build your marketing strategy with four key pillars:
- **Positioning** - Define your market position
- **ICP** - Identify your ideal customer profile
- **Messaging** - Craft compelling messages
- **Channel Strategy** - Choose the right channels

### ≡ƒºá Cognitive Engine (Advanced Business Context)
The core of RaptorFlow's intelligence is a stateful LangGraph-based analysis engine:
- **Stateful Workflows** - Multi-node graph orchestration for deep business analysis.
- **Gemini 1.5 Pro** - Powered by Google's latest long-context LLM via Vertex AI.
- **Strict Validation** - All AI outputs are validated against 20+ Pydantic models.
- **Iterative Refinement** - Analysis nodes for SWOT, PESTEL, Value Chain, and Brand Archetypes.
- **Enhanced ICPs** - Automatic enhancement of Ideal Customer Profiles with psychographic insights.
- **Messaging Strategy** - AI-generated core messaging and objection handling frameworks.

### ≡ƒæÑ Customer Cohorts
Manage customer segments with detailed analytics:
- **Segment definitions** - Detailed customer profiles
- **Pain points** - Customer challenges and needs
- **Channel preferences** - Where to reach each segment
- **Engagement metrics** - Track interaction rates

### ΓÜí Marketing Moves
Execute weekly marketing activities:
- **Task management** - Track individual marketing tasks
- **Progress tracking** - Monitor completion rates
- **Time estimation** - Plan your workload
- **Status management** - Update task states in real-time

### ≡ƒôó Campaign Management
Run successful multi-channel campaigns:
- **Campaign planning** - Set goals and budgets
- **Multi-channel execution** - LinkedIn, Email, Social Media
- **Performance tracking** - Monitor CTR, CPL, conversions
- **Budget management** - Track spend and ROI

### ≡ƒñû AI Content Generation (Muse)
Create marketing content with AI:
- **Content templates** - LinkedIn posts, emails, blog posts
- **Custom prompts** - Generate specific content types
- **Engagement tracking** - Monitor content performance
- **Content library** - Manage generated content

### ≡ƒôè Advanced Analytics
Get deep insights into your marketing:
- **Performance metrics** - Revenue, leads, conversions
- **Predictive analytics** - Forecast future performance
- **AI insights** - Get actionable recommendations
- **Funnel analysis** - Optimize conversion rates

### ≡ƒöö Real-time Notifications
Stay updated with live notifications:
- **Campaign updates** - Get notified about campaign changes
- **Task completions** - Track move completions
- **System alerts** - Monitor system health
- **Custom notifications** - Set up your own alerts

## ≡ƒ¢á∩╕Å Development

### Project Structure
```
raptorflow/
Γö£ΓöÇΓöÇ frontend/                 # Next.js frontend application
Γöé   Γö£ΓöÇΓöÇ src/
Γöé   Γöé   Γö£ΓöÇΓöÇ app/             # App Router pages
Γöé   Γöé   Γö£ΓöÇΓöÇ components/      # Reusable components
Γöé   Γöé   Γö£ΓöÇΓöÇ lib/            # Utilities and API clients
Γöé   Γöé   ΓööΓöÇΓöÇ styles/          # Global styles
Γöé   Γö£ΓöÇΓöÇ public/              # Static assets
Γöé   ΓööΓöÇΓöÇ package.json
Γö£ΓöÇΓöÇ backend/                  # FastAPI backend (optional)
Γöé   Γö£ΓöÇΓöÇ api/                 # API endpoints
Γöé   Γö£ΓöÇΓöÇ agents/              # AI agents
Γöé   Γö£ΓöÇΓöÇ skills/              # Marketing skills
Γöé   ΓööΓöÇΓöÇ tools/               # Integration tools
ΓööΓöÇΓöÇ docs/                    # Documentation
```

### Available Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server

# Testing
npm run test         # Run tests
npm run test:watch   # Run tests in watch mode

# Linting
npm run lint         # Run ESLint
npm run lint:fix     # Fix linting issues

# Type checking
npm run type-check   # Run TypeScript checks
```

### Environment Variables

Create a `.env.local` file in the frontend root:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Feature Flags
NEXT_PUBLIC_ENABLE_AI=true
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_NOTIFICATIONS=true

# Analytics (Optional)
NEXT_PUBLIC_GA_ID=your-google-analytics-id
NEXT_PUBLIC_SENTRY_DSN=your-sentry-dsn
```

## ≡ƒÜÇ Deployment

### Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### Docker
```bash
# Build Docker image
docker build -t raptorflow .

# Run container
docker run -p 3000:3000 raptorflow
```

### Static Export
```bash
# Build static version
npm run build
npm run export

# Deploy to any static host
```

For detailed deployment instructions, see [DEPLOYMENT_GUIDE.md](./frontend/DEPLOYMENT_GUIDE.md).

## ≡ƒôè Performance

### Core Metrics
- **Page Load Time**: < 2 seconds
- **First Contentful Paint**: < 1.5 seconds
- **Largest Contentful Paint**: < 2.5 seconds
- **Cumulative Layout Shift**: < 0.1

### Optimization Features
- Next.js Image Optimization
- Automatic code splitting
- Lazy loading for heavy components
- Efficient bundle size management
- CDN-ready static assets

## ≡ƒöÆ Security

### Implemented Measures
- HTTPS enforcement in production
- Input sanitization
- XSS protection
- CSRF protection
- Rate limiting
- Secure cookie handling

### Best Practices
- Regular dependency updates
- Security audits
- Environment variable protection
- API key management
- User data encryption

## ≡ƒñ¥ Contributing

We welcome contributions! Please see our [Contributing Guide](./CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Standards
- Use TypeScript for all new code
- Follow ESLint configuration
- Write meaningful commit messages
- Add documentation for new features

## ≡ƒôÜ Documentation

- [API Documentation](./docs/api.md)
- [Component Library](./docs/components.md)
- [Deployment Guide](./frontend/DEPLOYMENT_GUIDE.md)
- [Troubleshooting](./docs/troubleshooting.md)

## ≡ƒåÿ Support

### Getting Help
- **Help Center**: Built-in documentation and tutorials
- **FAQ**: Common questions and answers
- **Community**: Join our Discord community
- **Email**: support@raptorflow.com

### Reporting Issues
- **Bug Reports**: Use GitHub Issues
- **Feature Requests**: Submit via GitHub Discussions
- **Security Issues**: Email security@raptorflow.com

## ≡ƒôä License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## ≡ƒÖÅ Acknowledgments

- **Next.js Team** - For the amazing React framework
- **Tailwind CSS** - For the utility-first CSS framework
- **Framer Motion** - For smooth animations
- **Shadcn/ui** - For the beautiful component library
- **Our Contributors** - For making this project possible

## ≡ƒÄ» Roadmap

### Upcoming Features
- [ ] Advanced AI content generation
- [ ] Multi-language support
- [ ] Mobile app (React Native)
- [ ] Advanced integrations (HubSpot, Salesforce)
- [ ] Team collaboration features
- [ ] Custom branding options
- [ ] Advanced reporting dashboard
- [ ] API for third-party integrations

### Version History
- **v2.0.0** - Complete marketing operating system
- **v1.5.0** - Added AI content generation
- **v1.0.0** - Initial release with basic features

## ≡ƒô₧ Contact

- **Website**: [https://raptorflow.com](https://raptorflow.com)
- **Email**: hello@raptorflow.com
- **Twitter**: [@raptorflow](https://twitter.com/raptorflow)
- **LinkedIn**: [RaptorFlow](https://linkedin.com/company/raptorflow)

---

<div align="center">
  <p>Made with Γ¥ñ∩╕Å by the RaptorFlow Team</p>
  <p>Empowering founders to build successful marketing operations</p>
</div>
