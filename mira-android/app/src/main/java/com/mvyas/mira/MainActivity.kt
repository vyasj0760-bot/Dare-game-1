package com.mvyas.mira

import android.Manifest
import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.view.Gravity
import android.view.View
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView

class MainActivity : Activity() {
    private lateinit var status: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER_HORIZONTAL
            setPadding(dp(24), dp(32), dp(24), dp(24))
            setBackgroundColor(0xFFF5F7FC.toInt())
        }

        val title = TextView(this).apply {
            text = "Mira Companion"
            textSize = 28f
            setTextColor(0xFF20304A.toInt())
            gravity = Gravity.CENTER
        }
        val subtitle = TextView(this).apply {
            text = "Your lightweight floating anime companion"
            textSize = 14f
            setTextColor(0xFF65738A.toInt())
            gravity = Gravity.CENTER
            setPadding(0, dp(8), 0, dp(24))
        }
        status = TextView(this).apply {
            textSize = 14f
            setTextColor(0xFF34445C.toInt())
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, dp(24))
        }

        val permissionButton = button("Allow display over other apps") {
            if (!Settings.canDrawOverlays(this)) {
                val intent = Intent(
                    Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                    Uri.parse("package:$packageName")
                )
                startActivity(intent)
            } else {
                updateStatus()
            }
        }
        val startButton = button("Start floating Mira") {
            if (!Settings.canDrawOverlays(this)) {
                status.text = "First allow 'Display over other apps'."
                val intent = Intent(
                    Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                    Uri.parse("package:$packageName")
                )
                startActivity(intent)
            } else {
                startMira()
            }
        }
        val stopButton = button("Stop Mira") {
            stopService(Intent(this, MiraOverlayService::class.java))
            status.text = "Mira is stopped."
        }

        root.addView(title, matchWrap())
        root.addView(subtitle, matchWrap())
        root.addView(status, matchWrap())
        root.addView(permissionButton, matchWrap(dp(12)))
        root.addView(startButton, matchWrap(dp(12)))
        root.addView(stopButton, matchWrap(dp(12)))
        setContentView(root)
    }

    override fun onResume() {
        super.onResume()
        if (::status.isInitialized) updateStatus()
    }

    private fun startMira() {
        if (Build.VERSION.SDK_INT >= 33 &&
            checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != android.content.pm.PackageManager.PERMISSION_GRANTED
        ) {
            requestPermissions(arrayOf(Manifest.permission.POST_NOTIFICATIONS), 41)
        }
        val intent = Intent(this, MiraOverlayService::class.java)
        if (Build.VERSION.SDK_INT >= 26) startForegroundService(intent) else startService(intent)
        status.text = "Mira is running. Drag her around; tap to change animation."
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == 41 && Settings.canDrawOverlays(this)) {
            val intent = Intent(this, MiraOverlayService::class.java)
            if (Build.VERSION.SDK_INT >= 26) startForegroundService(intent) else startService(intent)
            status.text = "Mira is running. Notification permission can be changed in Settings."
        }
    }

    private fun updateStatus() {
        status.text = if (Settings.canDrawOverlays(this)) {
            "Overlay permission: allowed. Start Mira when you're ready."
        } else {
            "Overlay permission: not yet allowed."
        }
    }

    private fun button(label: String, action: () -> Unit): Button =
        Button(this).apply {
            text = label
            isAllCaps = false
            setOnClickListener { action() }
        }

    private fun matchWrap(top: Int = 0) =
        LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { topMargin = top }

    private fun dp(value: Int): Int =
        (value * resources.displayMetrics.density).toInt()
}
