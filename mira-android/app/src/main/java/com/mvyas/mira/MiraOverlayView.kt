package com.mvyas.mira

import android.content.Context
import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.Rect
import android.graphics.RectF
import android.os.SystemClock
import android.view.MotionEvent
import android.view.View
import kotlin.math.abs
import kotlin.math.sin

class MiraOverlayView(
    context: Context,
    private val onDrag: (Float, Float) -> Unit
) : View(context) {
    enum class Motion { IDLE, WALK, TALK }

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG or Paint.FILTER_BITMAP_FLAG)
    private val atlas = MiraSpriteCache.getAtlas(context)
    private val source = Rect()
    private val destination = RectF()
    private var motion = Motion.IDLE
    private var downX = 0f
    private var downY = 0f
    private var moved = false
    private var lastTap = 0L

    init {
        contentDescription = "Mira floating character. Tap to change animation, drag to move."
        isClickable = true
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val phase = (SystemClock.uptimeMillis() % 1200L) / 1200f
        val frame = when (motion) {
            Motion.IDLE -> (phase * 3f).toInt().coerceIn(0, 2)
            Motion.WALK -> 3 + ((phase * 6f).toInt() % 3)
            Motion.TALK -> 6 + ((phase * 6f).toInt() % 3)
        }

        // The atlas is a 3-column x 3-row sheet: idle, walk, and expressive poses.
        val cellWidth = atlas.width / 3
        val cellHeight = atlas.height / 3
        val column = frame % 3
        val row = frame / 3
        source.set(
            column * cellWidth,
            row * cellHeight,
            (column + 1) * cellWidth,
            (row + 1) * cellHeight
        )

        val bob = when (motion) {
            Motion.IDLE -> sin(phase * Math.PI * 2).toFloat() * dp(3)
            Motion.WALK -> abs(sin(phase * Math.PI * 4)).toFloat() * dp(5)
            Motion.TALK -> sin(phase * Math.PI * 5).toFloat() * dp(2)
        }
        val scalePulse = if (motion == Motion.TALK) {
            1f + sin(phase * Math.PI * 4).toFloat() * 0.012f
        } else 1f
        val drawWidth = width * scalePulse
        val drawHeight = height * scalePulse
        destination.set(
            (width - drawWidth) / 2f,
            (height - drawHeight) / 2f - bob,
            (width + drawWidth) / 2f,
            (height + drawHeight) / 2f - bob
        )
        canvas.drawBitmap(atlas, source, destination, paint)
        postInvalidateDelayed(100)
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                downX = event.rawX
                downY = event.rawY
                moved = false
                return true
            }
            MotionEvent.ACTION_MOVE -> {
                val dx = event.rawX - downX
                val dy = event.rawY - downY
                if (abs(dx) > dp(4) || abs(dy) > dp(4)) moved = true
                if (moved) {
                    onDrag(dx, dy)
                    downX = event.rawX
                    downY = event.rawY
                }
                return true
            }
            MotionEvent.ACTION_UP -> {
                if (!moved) {
                    motion = when (motion) {
                        Motion.IDLE -> Motion.WALK
                        Motion.WALK -> Motion.TALK
                        Motion.TALK -> Motion.IDLE
                    }
                    lastTap = SystemClock.uptimeMillis()
                    invalidate()
                }
                performClick()
                return true
            }
        }
        return true
    }

    override fun performClick(): Boolean {
        super.performClick()
        return true
    }

    private fun dp(value: Int): Float =
        value * resources.displayMetrics.density
}
