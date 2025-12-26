# Deployment Guide

This guide will help you deploy your Student Management System to the cloud so your friends can access it.

## ⚠️ Important Note About Vercel

**Vercel is NOT suitable for Flask applications.** Vercel is designed for:
- Static websites
- Serverless functions (Node.js, Python functions)
- Next.js, React, Vue static sites

Flask requires a persistent server, so you need a different platform.

## 🚀 Recommended Platforms

### Option 1: Railway (Easiest - Recommended) ⭐

Railway is the easiest platform to deploy Flask apps. It's free to start and very simple.

#### Steps:

1. **Create a Railway Account**
   - Go to https://railway.app
   - Sign up with GitHub (recommended)

2. **Prepare Your Code**
   - Make sure all files are committed to a GitHub repository
   - Push your code to GitHub

3. **Deploy on Railway**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will automatically detect it's a Python app

4. **Configure Environment Variables** (Optional but recommended)
   - Go to your project settings
   - Add environment variable:
     - `SECRET_KEY`: Generate a random secret key (you can use: `python -c "import secrets; print(secrets.token_hex(32))"`)

5. **Create Teacher Account**
   - After deployment, Railway will give you a URL like: `https://your-app.railway.app`
   - SSH into the Railway container or use Railway CLI to run:
     ```bash
     python create_teacher.py
     ```
   - Or add a route to create teacher on first run

6. **Access Your App**
   - Your app will be live at the Railway URL
   - Share this URL with your friends!

**Railway Free Tier:**
- $5 free credit monthly
- Enough for small apps
- Auto-deploys on git push

---

### Option 2: Render (Free Tier Available)

Render offers a free tier with some limitations.

#### Steps:

1. **Create a Render Account**
   - Go to https://render.com
   - Sign up with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your repository

3. **Configure Settings**
   - **Name**: student-management (or any name)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app`
   - **Plan**: Free (or paid for better performance)

4. **Environment Variables**
   - Add `SECRET_KEY` (generate one as mentioned above)

5. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy your app
   - Your app will be at: `https://your-app.onrender.com`

**Render Free Tier:**
- Free tier available
- Spins down after 15 minutes of inactivity (takes ~30 seconds to wake up)
- Good for testing and small projects

---

### Option 3: PythonAnywhere (Free Tier)

Good for learning, but has limitations.

#### Steps:

1. **Sign up at https://www.pythonanywhere.com**
2. **Upload your files** via Files tab
3. **Create a Web App** in the Web tab
4. **Configure WSGI file** to point to your app
5. **Run setup scripts** in the Console

---

## 🔧 Quick Setup Script

I'll create a script to help you set up the teacher account after deployment.

## 📝 Post-Deployment Checklist

After deploying:

1. ✅ Test the login page
2. ✅ Create teacher account (if not automated)
3. ✅ Test adding a student
4. ✅ Test creating a class
5. ✅ Share the URL with friends!

## 🔐 Security Notes

- **Change the SECRET_KEY** in production (use environment variable)
- The default SECRET_KEY in config.py is for development only
- Consider using PostgreSQL instead of SQLite for production (Railway provides this)

## 💡 Pro Tips

1. **Use Railway** - It's the easiest and most beginner-friendly
2. **Connect to GitHub** - Auto-deploys on every push
3. **Use Environment Variables** - Never commit secrets to GitHub
4. **Monitor Logs** - Check deployment logs if something goes wrong

## 🆘 Troubleshooting

**App won't start:**
- Check logs in your platform's dashboard
- Make sure `gunicorn` is in requirements.txt
- Verify Procfile is correct

**Database errors:**
- Make sure database is initialized
- Check if create_all() is being called
- For SQLite: ensure write permissions

**Can't access from other devices:**
- Make sure host is set to '0.0.0.0' (already done in run.py)
- Check firewall settings on the platform

---

## 🎯 Recommended: Railway Deployment

For the easiest experience, use **Railway**:
1. Sign up at railway.app
2. Connect GitHub repo
3. Deploy
4. Done!

Your app will be live in minutes! 🚀

