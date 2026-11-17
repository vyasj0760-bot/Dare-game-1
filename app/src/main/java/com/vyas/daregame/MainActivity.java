package com.vyas.daregame;
import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.JavascriptInterface;
import android.view.View;
import android.speech.tts.TextToSpeech;
import java.util.Locale;
import androidx.webkit.WebViewAssetLoader;
public class MainActivity extends Activity {
 private WebView webView; private WebViewAssetLoader assetLoader;
 private TextToSpeech tts; private boolean ttsReady=false;
 private class MayaBridge {
  @JavascriptInterface public void speak(final String message){runOnUiThread(()->{if(ttsReady&&tts!=null&&message!=null&&!message.trim().isEmpty()){tts.stop();tts.setLanguage(new Locale("hi","IN"));tts.speak(message,TextToSpeech.QUEUE_FLUSH,null,"maya-utterance");}});}
  @JavascriptInterface public void stop(){runOnUiThread(()->{if(tts!=null)tts.stop();});}
  @JavascriptInterface public boolean isReady(){return ttsReady;}
 }
 @Override public void onCreate(Bundle state){super.onCreate(state);
  tts=new TextToSpeech(this,status->{if(status==TextToSpeech.SUCCESS){int result=tts.setLanguage(new Locale("hi","IN"));ttsReady=result!=TextToSpeech.LANG_MISSING_DATA&&result!=TextToSpeech.LANG_NOT_SUPPORTED;}});
  assetLoader=new WebViewAssetLoader.Builder().addPathHandler("/assets/",new WebViewAssetLoader.AssetsPathHandler(this)).build();
  webView=new WebView(this);WebSettings settings=webView.getSettings();settings.setJavaScriptEnabled(true);settings.setDomStorageEnabled(true);settings.setDatabaseEnabled(true);settings.setMediaPlaybackRequiresUserGesture(true);settings.setAllowFileAccess(false);settings.setAllowContentAccess(false);settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
  webView.addJavascriptInterface(new MayaBridge(),"MayaTTS");
  webView.setWebViewClient(new WebViewClient(){@Override public android.webkit.WebResourceResponse shouldInterceptRequest(WebView view,android.webkit.WebResourceRequest request){return assetLoader.shouldInterceptRequest(request.getUrl());}});
  webView.setWebChromeClient(new WebChromeClient());webView.setOverScrollMode(View.OVER_SCROLL_NEVER);setContentView(webView);webView.loadUrl("https://appassets.androidplatform.net/assets/index.html");
 }
 @Override public void onBackPressed(){if(webView!=null&&webView.canGoBack())webView.goBack();else super.onBackPressed();}
 @Override protected void onDestroy(){if(tts!=null){tts.stop();tts.shutdown();}if(webView!=null)webView.destroy();super.onDestroy();}
}