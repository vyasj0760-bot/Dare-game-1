package com.mvyas.mira

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.LruCache

/**
 * The character atlas ships inside the APK. Decode once, then reuse the bitmap.
 * This avoids network downloads and repeated decode work during overlay redraws.
 */
object MiraSpriteCache {
    private val cache = object : LruCache<Int, Bitmap>(8 * 1024 * 1024) {
        override fun sizeOf(key: Int, value: Bitmap): Int = value.byteCount
    }

    fun preload(context: Context) {
        getAtlas(context)
    }

    fun getAtlas(context: Context): Bitmap {
        val key = R.drawable.mira_states
        synchronized(cache) {
            cache.get(key)?.let { return it }
            val options = BitmapFactory.Options().apply { inScaled = false }
            val bitmap = BitmapFactory.decodeResource(context.resources, key, options)
                ?: error("Mira sprite atlas could not be decoded")
            cache.put(key, bitmap)
            return bitmap
        }
    }
}
