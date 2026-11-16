package com.mvyas.mira

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.graphics.PixelFormat
import android.os.Build
import android.os.IBinder
import android.provider.Settings
import android.view.Gravity
import android.view.WindowManager

class MiraOverlayService : Service() {
    private var windowManager: WindowManager? = null
    private var miraView: MiraOverlayView? = null
    private var params: WindowManager.LayoutParams? = null

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        startForeground(NOTIFICATION_ID, buildNotification())
        MiraSpriteCache.preload(this)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (!Settings.canDrawOverlays(this)) {
            stopSelf()
            return START_NOT_STICKY
        }
        if (miraView == null) attachOverlay()
        return START_STICKY
    }

    private fun attachOverlay() {
        windowManager = getSystemService(WINDOW_SERVICE) as WindowManager
        val density = resources.displayMetrics.density
        val overlayParams = WindowManager.LayoutParams(
            (124 * density).toInt(),
            (158 * density).toInt(),
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
                WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.TOP or Gravity.START
            x = (12 * density).toInt()
            y = (180 * density).toInt()
        }
        params = overlayParams

        miraView = MiraOverlayView(this) { dx, dy ->
            params?.let { layout ->
                layout.x += dx.toInt()
                layout.y += dy.toInt()
                miraView?.let { view ->
                    try {
                        windowManager?.updateViewLayout(view, layout)
                    } catch (_: IllegalArgumentException) {
                        // Overlay was already removed by the system.
                    }
                }
            }
        }
        miraView?.let { view -> windowManager?.addView(view, overlayParams) }
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= 26) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Mira floating companion",
                NotificationManager.IMPORTANCE_LOW
            )
            getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
        }
    }

    private fun buildNotification(): Notification {
        val openApp = PendingIntent.getActivity(
            this,
            0,
            Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        return if (Build.VERSION.SDK_INT >= 26) {
            Notification.Builder(this, CHANNEL_ID)
                .setSmallIcon(android.R.drawable.ic_dialog_info)
                .setContentTitle("Mira is active")
                .setContentText("Tap to open Mira settings. Use Stop Mira to close the overlay.")
                .setContentIntent(openApp)
                .setOngoing(true)
                .build()
        } else {
            @Suppress("DEPRECATION")
            Notification.Builder(this)
                .setSmallIcon(android.R.drawable.ic_dialog_info)
                .setContentTitle("Mira is active")
                .setContentText("Floating companion is running.")
                .setOngoing(true)
                .build()
        }
    }

    override fun onDestroy() {
        miraView?.let {
            try {
                windowManager?.removeView(it)
            } catch (_: IllegalArgumentException) {
            }
        }
        miraView = null
        stopForeground(STOP_FOREGROUND_REMOVE)
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    companion object {
        private const val CHANNEL_ID = "mira_overlay"
        private const val NOTIFICATION_ID = 7001
    }
}
