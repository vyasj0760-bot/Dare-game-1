package com.mvyas.mira

import android.content.Context
import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.Rect
import android.graphics.RectF
import android.os.SystemClock
import android.view.MotionEvent
import android.view.View
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
            Motion.IDLE -> 0
            Motion.WALK -> 1
            Motion.TALK -> 2
        }
        val frameWidth = atlas.width / 3
        source.set(frame * frameWidth, 0, (frame + 1) * frameWidth, atlas.height)

        val bob = when (motion) {
            Motion.IDLE -> sin(phase * Math.PI * 2).toFloat() * dp(3)
            Motion.WALK -> kotlin.math.abs(sin(phase * Math.PI * 4)).toFloat() * dp(5)
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
        postInvalidateDelayed(70)
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
                if (kotlin.math.abs(dx) > dp(4) || kotlin.math.abs(dy) > dp(4)) moved = true
                if (moved) {
                    onDrag(dx, dy)
                    downX = event.rawX
                    downY = event.rawY
                }
                return true
            }
            MotionEvent.ACTION_UP -> {
                if (!moved) {
                    val now = SystemClock.uptimeMillis()
                    motion = if (now - lastTap < 500L) {
                        Motion.TALK
                    } else {
                        when (motion) {
                            Motion.IDLE -> Motion.WALK
                            Motion.WALK -> Motion.TALK
                            Motion.TALK -> Motion.IDLE
                        }
                    }
                    lastTap = now
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
