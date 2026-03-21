# Frontend Deployment Guide

Guide for deploying the React frontend application to Render.

## 📋 Prerequisites

- GitHub account with the code repository
- Render account (https://render.com)
- Node.js 14+ installed locally (for testing builds)

## 🎯 Step-by-Step Deployment

### Step 1: Connect GitHub Repository

1. Log in to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** button
3. Select **Static Site**
4. Click **Connect a repository**
5. Select **GitHub** and authorize Render
6. Choose your repository: `klb2006/IOT-TASK-LEELA`
7. Click **Connect**

### Step 2: Configure Build Settings

| Setting | Value |
|---------|-------|
| **Name** | `iot-water-tank-frontend` |
| **Branch** | `main` |
| **Build Command** | `cd frontend && npm install && npm run build` |
| **Publish Directory** | `frontend/dist` |

### Step 3: Add Environment Variables

1. Go to **Environment** tab
2. Add the following variables:

```
VITE_API_URL=https://your-backend-url.onrender.com
```

Replace `your-backend-url` with your actual backend service URL from Render.

### Step 4: Deploy

1. Click **Create Static Site**
2. Render will automatically start the build
3. Wait for the deployment to complete (usually 2-5 minutes)
4. Your site will be live at the Render-provided URL

## 🔗 Getting Your Frontend URL

After deployment:
1. Go to Render Dashboard → Static Sites
2. Click on your `iot-water-tank-frontend` service
3. Copy the URL from the page (e.g., `https://iot-water-tank-frontend.onrender.com`)

**Update your backend CORS settings** with this URL to allow requests!

## 🔄 Updating Backend API URL

If you haven't set up the backend yet:

1. After backend is deployed, update the environment variable:
   - Go to **Settings** → **Environment**
   - Update `VITE_API_URL` to your backend URL
   - Render will automatically rebuild and redeploy

Example backend URL: `https://your-backend-service.onrender.com`

## 📝 Build Command Explanation

```bash
cd frontend && npm install && npm run build
```

This command:
1. Navigates to `frontend/` directory
2. Installs all npm dependencies
3. Creates optimized production build in `frontend/dist/`

## ✅ Testing Before Deployment

Test locally to ensure everything works:

```bash
cd frontend
npm install
npm run build
npm run preview  # Preview the production build
```

Open browser to `http://localhost:4173` to test.

## 🛠️ Troubleshooting

### Build Fails with "Module not found"

**Solution:**
- Ensure `package.json` exists in `frontend/` directory
- Check `package-lock.json` is correct
- Clear npm cache: `npm cache clean --force`

### API Requests Fail with CORS Error

**Solution:**
1. Verify `VITE_API_URL` environment variable is set correctly
2. Ensure backend CORS allows your frontend URL
3. Check backend is running and accessible

### Blank Page After Deployment

**Solution:**
1. Check browser console for errors (F12)
2. Verify API URL is correct
3. Check if backend is returning data

To debug:
1. Go to Render Dashboard
2. Click your frontend service
3. View **Logs** tab for error messages

## 🚀 Deployment Checklist

- [ ] GitHub repository pushed with latest code
- [ ] Render account created and authenticated
- [ ] Build command set to: `cd frontend && npm install && npm run build`
- [ ] Publish directory set to: `frontend/dist`
- [ ] Environment variable `VITE_API_URL` configured
- [ ] Backend URL is accessible and CORS configured
- [ ] Build completes successfully (check Render Logs)
- [ ] Frontend loads in browser
- [ ] API calls work (check browser Network tab)
- [ ] Water tank animation displays correctly
- [ ] Sensor data updates every 15 seconds

## 📊 Performance Tips

1. **Minification** - Already enabled in build process
2. **Lazy Loading** - React Router handles this automatically
3. **Images** - Store in `public/` for best performance
4. **Cache** - Render automatically caches builds

## 🔄 Redeployment

Every time you push to GitHub:
1. Render automatically detects changes
2. Triggers new build
3. Deploys if build succeeds

Manual redeploy:
1. Render Dashboard → Select your service
2. Click **Deploys** tab
3. Find latest deploy → Click **Redeploy**

## 📞 Need Help?

- Check [Render Documentation](https://render.com/docs)
- Review build logs in Render Dashboard
- Ensure local build works: `npm run build`

## ✨ Next Steps

After frontend is deployed:
1. Deploy backend (see BACKEND_DEPLOYMENT.md)
2. Update frontend `VITE_API_URL` with backend URL
3. Test complete application end-to-end
4. Monitor logs for errors
