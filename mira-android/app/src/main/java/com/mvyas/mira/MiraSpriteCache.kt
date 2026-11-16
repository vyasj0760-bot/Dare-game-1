package com.mvyas.mira

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.LruCache

/**
 * The character atlas is bundled in the APK and decoded once.
 * LruCache keeps the decoded bitmap in memory so redraws do not decode it again.
 */
object MiraSpriteCache {
    private val cache = object : LruCache<Int, Bitmap>(4 * 1024 * 1024) {}

    fun preload(context: Context) {
        getAtlas(context)
    }

    fun getAtlas(context: Context): Bitmap {
        val key = R.drawable.mira_states
        synchronized(cache) {
            cache.get(key)?.let { return it }
            val options = BitmapFactory.Options().apply { inScaled = false }
            val bitmap = BitmapFactory.decodeResource(
                context.resources,
                key,
                options
            ) ?: error("Mira sprite atlas could not be decoded")
            cache.put(key, bitmap)
            return bitmap
        }
    }
}
