# 🚀 RaptorFlow - Marketing Operating System

> **The complete marketing operating system for founders and marketing teams**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Next.js](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4-38B2AC)](https://tailwindcss.com/)

## 🎯 Overview

RaptorFlow is a comprehensive marketing operating system designed specifically for founders and marketing teams. It provides everything you need to manage your entire marketing workflow - from strategic foundation to AI-powered content generation, campaign management, and advanced analytics.

### ✨ Key Features

- 🏗️ **Marketing Foundation** - Build your strategic marketing pillars
- 👥 **Customer Cohorts** - Manage and analyze customer segments
- ⚡ **Marketing Moves** - Track weekly marketing execution
- 📢 **Campaign Management** - Run multi-channel marketing campaigns
- 🤖 **AI Content Generation** - Create marketing content with AI
- 📊 **Advanced Analytics** - Get insights and predictive analytics
- 🔔 **Real-time Notifications** - Stay updated with live alerts
- ⚙️ **Comprehensive Settings** - Customize your experience
- 📚 **Help Center** - Get support and learn best practices

## 🚀 Quick Start

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

## 🏗️ Architecture

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

## 📱 Features Deep Dive

### 🏗️ Marketing Foundation
Build your marketing strategy with four key pillars:
- **Positioning** - Define your market position
- **ICP** - Identify your ideal customer profile
- **Messaging** - Craft compelling messages
- **Channel Strategy** - Choose the right channels

### 👥 Customer Cohorts
Manage customer segments with detailed analytics:
- **Segment definitions** - Detailed customer profiles
- **Pain points** - Customer challenges and needs
- **Channel preferences** - Where to reach each segment
- **Engagement metrics** - Track interaction rates

### ⚡ Marketing Moves
Execute weekly marketing activities:
- **Task management** - Track individual marketing tasks
- **Progress tracking** - Monitor completion rates
- **Time estimation** - Plan your workload
- **Status management** - Update task states in real-time

### 📢 Campaign Management
Run successful multi-channel campaigns:
- **Campaign planning** - Set goals and budgets
- **Multi-channel execution** - LinkedIn, Email, Social Media
- **Performance tracking** - Monitor CTR, CPL, conversions
- **Budget management** - Track spend and ROI

### 🤖 AI Content Generation (Muse)
Create marketing content with AI:
- **Content templates** - LinkedIn posts, emails, blog posts
- **Custom prompts** - Generate specific content types
- **Engagement tracking** - Monitor content performance
- **Content library** - Manage generated content

### 📊 Advanced Analytics
Get deep insights into your marketing:
- **Performance metrics** - Revenue, leads, conversions
- **Predictive analytics** - Forecast future performance
- **AI insights** - Get actionable recommendations
- **Funnel analysis** - Optimize conversion rates

### 🔔 Real-time Notifications
Stay updated with live notifications:
- **Campaign updates** - Get notified about campaign changes
- **Task completions** - Track move completions
- **System alerts** - Monitor system health
- **Custom notifications** - Set up your own alerts

## 🛠️ Development

### Project Structure
```
raptorflow/
├── frontend/                 # Next.js frontend application
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   ├── components/      # Reusable components
│   │   ├── lib/            # Utilities and API clients
│   │   └── styles/          # Global styles
│   ├── public/              # Static assets
│   └── package.json
├── backend/                  # FastAPI backend (optional)
│   ├── api/                 # API endpoints
│   ├── agents/              # AI agents
│   ├── skills/              # Marketing skills
│   └── tools/               # Integration tools
└── docs/                    # Documentation
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

## 🚀 Deployment

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

## 📊 Performance

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

## 🔒 Security

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

## 🤝 Contributing

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

## 📚 Documentation

- [API Documentation](./docs/api.md)
- [Component Library](./docs/components.md)
- [Deployment Guide](./frontend/DEPLOYMENT_GUIDE.md)
- [Troubleshooting](./docs/troubleshooting.md)

## 🆘 Support

### Getting Help
- **Help Center**: Built-in documentation and tutorials
- **FAQ**: Common questions and answers
- **Community**: Join our Discord community
- **Email**: support@raptorflow.com

### Reporting Issues
- **Bug Reports**: Use GitHub Issues
- **Feature Requests**: Submit via GitHub Discussions
- **Security Issues**: Email security@raptorflow.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 🙏 Acknowledgments

- **Next.js Team** - For the amazing React framework
- **Tailwind CSS** - For the utility-first CSS framework
- **Framer Motion** - For smooth animations
- **Shadcn/ui** - For the beautiful component library
- **Our Contributors** - For making this project possible

## 🎯 Roadmap

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

## 📞 Contact

- **Website**: [https://raptorflow.com](https://raptorflow.com)
- **Email**: hello@raptorflow.com
- **Twitter**: [@raptorflow](https://twitter.com/raptorflow)
- **LinkedIn**: [RaptorFlow](https://linkedin.com/company/raptorflow)

---

<div align="center">
  <p>Made with ❤️ by the RaptorFlow Team</p>
  <p>Empowering founders to build successful marketing operations</p>
</div>
