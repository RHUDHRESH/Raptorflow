# RaptorFlow Actual Architecture Documentation

## 🏗️ **Current Architecture Overview**

RaptorFlow uses a **modern serverless architecture** with clear separation between frontend and backend services.

---

## 📋 **Technology Stack**

### **Frontend (Vercel)**
- **Framework**: Next.js 16.1.1 with React 19.2.3
- **Deployment**: Vercel (serverless)
- **Styling**: Tailwind CSS 4.0
- **UI Components**: Radix UI
- **State Management**: Zustand 5.0.9
- **Animations**: GSAP + Framer Motion
- **Testing**: Playwright
- **TypeScript**: Full TypeScript support

### **Backend (Render/Serverless)**
- **Framework**: FastAPI (Python)
- **Deployment**: Render (or similar serverless platform)
- **Database**: Supabase (PostgreSQL)
- **Cache**: Upstash Redis
- **AI/ML**: Vertex AI (Google Cloud)
- **Storage**: Google Cloud Storage (GCS)
- **Email**: Resend
- **Monitoring**: Sentry

### **Infrastructure**
- **Frontend Hosting**: Vercel
- **Backend Hosting**: Render (serverless)
- **Database**: Supabase (managed PostgreSQL)
- **Cache**: Upstash Redis (managed Redis)
- **File Storage**: Google Cloud Storage
- **AI/ML**: Vertex AI (Google Cloud)
- **Email**: Resend
- **Domain**: Custom domain with HTTPS

---

## 🔗 **Service Integration**

### **API Communication**
```
Frontend (Vercel) → API Proxy → Backend (Render)
```

- **Frontend** runs on Vercel
- **Backend** runs on Render (or similar)
- **API Proxy** handles cross-origin requests
- **CORS** properly configured for security

### **Data Flow**
```
User → Frontend (Vercel) → API Proxy → Backend (Render) → Supabase/Upstash/Vertex AI
```

---

## 🗄️ **Database & Storage**

### **Supabase (PostgreSQL)**
- **Primary Database**: User data, workspaces, campaigns
- **Authentication**: Built-in Supabase Auth
- **Real-time**: Real-time subscriptions
- **Row Level Security**: Enabled for data isolation

### **Upstash Redis**
- **Session Storage**: User sessions and temporary data
- **Rate Limiting**: API rate limiting
- **Cache**: Frequently accessed data
- **Real-time**: Pub/Sub for real-time features

### **Google Cloud Storage**
- **File Storage**: User uploads, documents, images
- **Static Assets**: Large files, media content
- **Backups**: Database backups and exports
- **CDN**: Global file distribution

---

## 🤖 **AI/ML Integration**

### **Vertex AI (Google Cloud)**
- **Primary Model**: Gemini 2.0 Flash Experimental
- **Inference**: Text generation, analysis, processing
- **API Key**: Vertex AI API key for authentication
- **Location**: us-central1 (default)

### **AI Features**
- **Content Generation**: AI-powered content creation
- **Data Analysis**: AI-driven insights and recommendations
- **Natural Language**: Conversational interfaces
- **Image Processing**: OCR and image analysis

---

## 📧 **Communication Services**

### **Resend (Email)**
- **Transactional Emails**: User notifications, alerts
- **Marketing Emails**: Campaign communications
- **Templates**: Pre-designed email templates
- **Domain**: Custom domain for email delivery

### **Webhooks**
- **Payment Processing**: PhonePe payment notifications
- **User Events**: Real-time user activity tracking
- **System Events**: Backend system notifications

---

## 🔐 **Security Architecture**

### **Authentication**
- **Primary**: Supabase Auth (JWT tokens)
- **Session Management**: Upstash Redis
- **Social Login**: Google, GitHub integration
- **Password Reset**: Secure email-based reset

### **Data Security**
- **Encryption**: Data at rest and in transit
- **Row Level Security**: Database-level access control
- **API Security**: Rate limiting, CORS, input validation
- **Environment Variables**: Secure secret management

---

## 📊 **Monitoring & Observability**

### **Sentry (Error Tracking)**
- **Frontend Errors**: JavaScript errors and exceptions
- **Backend Errors**: Python exceptions and API errors
- **Performance**: Response times and user experience
- **Release Tracking**: Deployment and version monitoring

### **Health Checks**
- **API Health**: Backend service health monitoring
- **Database Health**: Supabase connection monitoring
- **Cache Health**: Upstash Redis monitoring
- **External Services**: Third-party service monitoring

---

## 🚀 **Deployment Architecture**

### **Frontend Deployment (Vercel)**
```
Git Push → Vercel Build → Deploy → Global CDN
```

- **Build Process**: Next.js build optimization
- **Static Assets**: Optimized and cached
- **Serverless Functions**: API routes and server-side rendering
- **Edge Network**: Global distribution

### **Backend Deployment (Render)**
```
Git Push → Render Build → Deploy → Serverless Container
```

- **Build Process**: FastAPI application build
- **Container**: Docker container with Python runtime
- **Serverless**: Auto-scaling based on demand
- **Health Checks**: Automated health monitoring

---

## 🔄 **Development Workflow**

### **Local Development**
```bash
# Frontend
cd frontend
npm run dev

# Backend  
cd backend
python -m uvicorn main:app --reload

# Database
supabase start

# Redis (Upstash - no local setup needed)
```

### **Environment Setup**
- **Frontend**: `.env.local` for local development
- **Backend**: `.env` for local development
- **Database**: Supabase local development
- **Cache**: Upstash Redis (no local setup)

---

## 📁 **Project Structure**

```
raptorflow/
├── frontend/                 # Next.js frontend (Vercel)
│   ├── src/
│   │   ├── app/             # App router pages
│   │   ├── components/      # React components
│   │   ├── lib/            # Utility functions
│   │   └── api/            # API routes (proxy)
│   ├── public/             # Static assets
│   ├── package.json        # Frontend dependencies
│   └── vercel.json         # Vercel configuration
├── backend/                 # FastAPI backend (Render)
│   ├── api/                # API endpoints
│   ├── agents/             # AI agents
│   ├── core/               # Core functionality
│   ├── services/           # External services
│   ├── main.py             # FastAPI application
│   └── requirements.txt    # Python dependencies
├── supabase/                # Database schema and migrations
├── docs/                    # Documentation
└── README.md               # Project documentation
```

---

## 🔧 **Configuration Files**

### **Frontend Configuration**
- `vercel.json` - Vercel deployment configuration
- `package.json` - Frontend dependencies and scripts
- `.env.local` - Local development environment variables
- `next.config.js` - Next.js configuration
- `tailwind.config.js` - Tailwind CSS configuration

### **Backend Configuration**
- `requirements.txt` - Python dependencies
- `.env` - Local development environment variables
- `main.py` - FastAPI application entry point
- `Dockerfile` - Container configuration (if needed)

---

## 🌐 **API Architecture**

### **Frontend API Routes**
- `/api/auth/*` - Authentication endpoints
- `/api/proxy/*` - Backend proxy routes
- `/api/webhooks/*` - Webhook handlers

### **Backend API Routes**
- `/api/v1/auth/*` - Authentication and user management
- `/api/v1/workspaces/*` - Workspace management
- `/api/v1/campaigns/*` - Campaign management
- `/api/v1/agents/*` - AI agent endpoints
- `/api/v1/analytics/*` - Analytics and reporting

### **API Communication**
```
Frontend → /api/proxy/* → Backend API
```

The proxy route handles cross-origin requests and forwards them to the backend server.

---

## 🎯 **Key Features**

### **User Management**
- **Authentication**: Supabase Auth with social login
- **Profiles**: User profiles and preferences
- **Workspaces**: Multi-tenant workspace management
- **Permissions**: Role-based access control

### **AI-Powered Features**
- **Content Generation**: AI-powered content creation
- **Data Analysis**: AI-driven insights and recommendations
- **Natural Language**: Conversational interfaces
- **Automation**: Automated workflows and processes

### **Real-time Features**
- **Collaboration**: Real-time collaboration tools
- **Notifications**: Real-time notifications and alerts
- **Updates**: Live data updates and synchronization
- **Chat**: Real-time messaging and communication

---

## 📈 **Performance Optimization**

### **Frontend Optimization**
- **Code Splitting**: Automatic code splitting with Next.js
- **Image Optimization**: Next.js Image optimization
- **Caching**: Browser and CDN caching
- **Bundle Size**: Optimized bundle sizes

### **Backend Optimization**
- **Database Optimization**: Query optimization and indexing
- **Caching**: Redis caching for frequently accessed data
- **Rate Limiting**: API rate limiting and throttling
- **Connection Pooling**: Database connection pooling

---

## 🔍 **Monitoring & Debugging**

### **Error Tracking**
- **Sentry**: Comprehensive error tracking and monitoring
- **Logs**: Structured logging for debugging
- **Performance**: Response time and performance monitoring
- **Health Checks**: Automated health monitoring

### **Development Tools**
- **Hot Reload**: Fast development with hot reload
- **TypeScript**: Type safety and better development experience
- **ESLint**: Code quality and consistency
- **Testing**: Automated testing with Playwright

---

## 🚀 **Deployment Strategy**

### **Continuous Deployment**
- **Frontend**: Automatic deployment on Git push to Vercel
- **Backend**: Automatic deployment on Git push to Render
- **Database**: Supabase migrations and schema updates
- **Monitoring**: Automated monitoring and alerting

### **Environment Management**
- **Development**: Local development environment
- **Staging**: Staging environment for testing
- **Production**: Production environment with full monitoring
- **Configuration**: Environment-specific configuration management

---

## 📚 **Best Practices**

### **Code Quality**
- **TypeScript**: Full TypeScript coverage
- **ESLint**: Code quality and consistency
- **Testing**: Comprehensive test coverage
- **Documentation**: Clear and comprehensive documentation

### **Security**
- **Authentication**: Secure authentication and authorization
- **Data Protection**: Data encryption and protection
- **API Security**: API security best practices
- **Environment Variables**: Secure secret management

### **Performance**
- **Optimization**: Performance optimization techniques
- **Caching**: Effective caching strategies
- **Monitoring**: Performance monitoring and optimization
- **Scalability**: Scalable architecture design

---

## 🔄 **Future Enhancements**

### **Planned Features**
- **Advanced AI**: More sophisticated AI features
- **Mobile App**: Native mobile applications
- **API v2**: Enhanced API with more features
- **Analytics**: Advanced analytics and reporting

### **Infrastructure Improvements**
- **Edge Computing**: Edge computing for better performance
- **Microservices**: Microservices architecture for scalability
- **Advanced Monitoring**: Enhanced monitoring and observability
- **Automation**: Increased automation and CI/CD improvements

---

## 📞 **Support & Contact**

### **Documentation**
- **API Documentation**: Comprehensive API documentation
- **User Guides**: User guides and tutorials
- **Developer Docs**: Developer documentation
- **Troubleshooting**: Common issues and solutions

### **Community**
- **GitHub**: Open source contributions and issues
- **Discord**: Community support and discussions
- **Blog**: Updates and announcements
- **Newsletter**: Regular updates and news

---

## 🎉 **Summary**

RaptorFlow uses a **modern, scalable, and secure architecture** with:

- **Frontend**: Next.js on Vercel with modern React patterns
- **Backend**: FastAPI on Render with Python
- **Database**: Supabase PostgreSQL with real-time features
- **Cache**: Upstash Redis for performance
- **AI**: Vertex AI for intelligent features
- **Storage**: Google Cloud Storage for file management
- **Email**: Resend for communication
- **Monitoring**: Sentry for error tracking

This architecture provides **high performance**, **scalability**, **security**, and **developer experience** while maintaining **cost-effectiveness** and **reliability**.
