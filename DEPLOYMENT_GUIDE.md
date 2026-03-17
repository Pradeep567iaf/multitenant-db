# Free Deployment Guide for Multi-Tenant System

## 🚀 Option 1: Render + Supabase (Recommended)

### Step 1: Prepare Your Code
1. Push your code to GitHub
2. Make sure `.gitignore` excludes sensitive files:
   ```
   .env
   __pycache__/
   *.pyc
   env/
   ```

### Step 2: Setup Supabase (Free PostgreSQL)
1. Go to https://supabase.com
2. Sign up/Login
3. Create new project
4. Get your database connection string:
   - Settings → Database → Connection Info
   - Copy the connection string (it looks like):
     `postgresql://postgres:[PASSWORD]@[HOST]:[PORT]/[DATABASE]`

### Step 3: Deploy to Render
1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name**: `multitenant-system`
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Root Directory**: Leave empty
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements-prod.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

6. Add Environment Variables:
   ```
   DATABASE_URL=your_supabase_connection_string
   SECRET_KEY_SUPERADMIN=generate_strong_secret_here
   SECRET_KEY_TENANT=generate_different_strong_secret_here
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your_email@gmail.com
   SMTP_PASSWORD=your_gmail_app_password
   EMAIL_FROM=noreply@yourdomain.com
   ```

7. Click "Create Web Service"

### Step 4: Initialize Database
1. Once deployed, get your Render app URL
2. SSH into your Render service or run init script locally with production DB URL
3. Run the database initialization script

---

## 🚂 Option 2: Railway + Supabase

### Step 1: Setup Railway
1. Go to https://railway.app
2. Sign up/Login
3. Click "Start a New Project"
4. Choose "Deploy from GitHub repo"
5. Select your repository

### Step 2: Configure
1. Railway will auto-detect Python
2. Add environment variables in Railway dashboard
3. Add PostgreSQL plugin (or use Supabase separately)

### Step 3: Deploy
1. Railway auto-deploys on git push
2. Get your deployed URL from Railway dashboard

---

## ☁️ Option 3: Vercel + Neon.tech

### Step 1: Setup Neon.tech
1. Go to https://neon.tech
2. Create free PostgreSQL database
3. Get connection string

### Step 2: Deploy to Vercel
1. Go to https://vercel.com
2. Import your GitHub repository
3. Add environment variables
4. Deploy

---

## 🔐 Security Considerations

### Generate Strong Secrets:
```bash
# Generate secure keys (run locally)
python -c "import secrets; print(secrets.token_hex(32))"
```

### Environment Variables to Set:
- `DATABASE_URL` - From your cloud database
- `SECRET_KEY_SUPERADMIN` - Strong random string
- `SECRET_KEY_TENANT` - Different strong random string
- `SMTP_*` - Your email credentials
- `ALLOWED_ORIGINS` - Your frontend domains

---

## 🌐 Custom Domain (Optional)

### Render:
1. In Render dashboard, go to your service
2. Click "Settings" → "Custom Domains"
3. Add your domain
4. Update DNS records as instructed

### Railway:
1. Go to your project settings
2. Add custom domain
3. Update DNS CNAME record

---

## 📊 Monitoring

### Free Monitoring Tools:
- **Render**: Built-in logs and metrics
- **UptimeRobot**: Free uptime monitoring
- **LogSnag**: Free log aggregation

---

## 💰 Free Tier Limits

### Render:
- 750 free hours/month (~25 days)
- Sleeps after 15 minutes of inactivity
- 512MB RAM

### Supabase:
- 500MB database
- 2GB bandwidth/month
- 50,000 rows

### Railway:
- $5 credit/month
- Sleeps after inactivity
- 1GB RAM

---

## 🔄 CI/CD Setup

### Auto-deploy on Git Push:
All platforms support automatic deployment when you push to main branch.

### GitHub Actions (Optional):
Create `.github/workflows/deploy.yml` for custom deployment workflows.

---

## 🛠️ Troubleshooting

### Common Issues:
1. **Database Connection**: Check DATABASE_URL format
2. **Environment Variables**: Ensure all required vars are set
3. **CORS Errors**: Update ALLOWED_ORIGINS
4. **Sleeping Services**: First request may be slow

### Logs:
- Render: Dashboard → Logs
- Railway: Dashboard → Logs
- Vercel: Dashboard → Logs

---

## 🎉 Success!

Once deployed, your API will be available at:
- Render: `https://your-app.onrender.com`
- Railway: `https://your-app.up.railway.app`
- Vercel: `https://your-app.vercel.app`

Access documentation at: `https://your-domain.com/docs`
