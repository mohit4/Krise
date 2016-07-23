package application.com.krise.utils;

import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.Bundle;
import android.support.v4.app.NotificationCompat;
import android.support.v4.content.LocalBroadcastManager;

import application.com.krise.R;
import application.com.krise.views.Home;
import application.com.krise.views.SplashScreen;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.zip.Inflater;

public class NotificationManager {
    private static NotificationManager notificationManager;
    private Context context;
    private SharedPreferences prefs;
    private android.app.NotificationManager mNotificationManager;
    NotificationCompat.Builder builder;
    public static int notificationId ;
    public static final int NOTIFICATION_ID_MESSAGE = 1;
    public static final int NOTIFICATION_ID_FEED = 2;
    private NotificationManager(Context context) {
        this.context = context;
    }

    public static NotificationManager getInstance(Context context)
    {
        if(null== notificationManager) {
            notificationManager = new NotificationManager(context);
        }
        return notificationManager;
    }

    public void sendNotification(Bundle extras) {
        if(prefs == null)
            prefs = context.getSharedPreferences("application_settings", 0);
        String msg = extras.getString("Notification");
        String type = extras.getString("type");
        String command = extras.getString("command");
        Intent notificationActivity = null;
        boolean showNotification = true;


        Uri soundUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
        NotificationCompat.Builder mBuilder = null;
        if (type != null && type.equals(CommonLib.DISASTER_NOTIFICATION)) {
            notificationId = NOTIFICATION_ID_MESSAGE;
            JSONObject message = null;
            String title = "", description = "";

            try {
                message = new JSONObject(msg);

                if(message.has("title")) {
                    title = String.valueOf(message.get("title"));
                }

                if(message.has("message")) {
                    description = String.valueOf(message.get("message"));
                }

                Intent intent = new Intent(CommonLib.LOCAL_PUSH_PROMOTIONAL_BROADCAST);
                intent.putExtra("title",title);
                intent.putExtra("message", description);

                LocalBroadcastManager.getInstance(context).sendBroadcast(intent);


            } catch (JSONException e) {
                e.printStackTrace();
            }

            mBuilder = new NotificationCompat.Builder(context).setSmallIcon(getNotificationIcon())
                    .setContentTitle(title).setStyle(new NotificationCompat.BigTextStyle().bigText(description))
                    .setAutoCancel(true).setContentText(description).setSound(soundUri);
        } else {
            notificationId = NOTIFICATION_ID_MESSAGE;
            JSONObject message = null;
            String title = "", description = "";

            try {
                message = new JSONObject(msg);

                if(message.has("title")) {
                    title = String.valueOf(message.get("title"));
                }

                if(message.has("message")) {
                    description = String.valueOf(message.get("message"));
                }

                Intent intent = new Intent(CommonLib.LOCAL_PUSH_PROMOTIONAL_BROADCAST);
                intent.putExtra("title",title);
                intent.putExtra("message", description);

                LocalBroadcastManager.getInstance(context).sendBroadcast(intent);

            } catch (JSONException e) {
                e.printStackTrace();
            }

            mBuilder = new NotificationCompat.Builder(context).setSmallIcon(getNotificationIcon())
                    .setContentTitle(title).setStyle(new NotificationCompat.BigTextStyle().bigText(description))
                    .setAutoCancel(true).setContentText(description).setSound(soundUri);
        }
        // check if app is alive, do not push the message notifiication then
        mNotificationManager = (android.app.NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
        if (notificationActivity == null)
            notificationActivity = new Intent(context, Home.class);
        int flags = PendingIntent.FLAG_CANCEL_CURRENT;
        PendingIntent contentIntent = PendingIntent.getActivity(context, 0, notificationActivity, flags);
        if(mBuilder == null)
            mBuilder = new NotificationCompat.Builder(context).setSmallIcon(getNotificationIcon())
                    .setContentTitle("Krise").setStyle(new NotificationCompat.BigTextStyle().bigText(msg))
                    .setAutoCancel(true).setContentText(msg).setSound(soundUri);
        mBuilder.setContentIntent(contentIntent);
        if (showNotification)
            mNotificationManager.notify(notificationId, mBuilder.build());
    }

    public void cancelNotification(int notificationId)
    {
        mNotificationManager.cancel(notificationId);
    }

    private int getNotificationIcon() {
        boolean useWhiteIcon = (android.os.Build.VERSION.SDK_INT >= 21);
        return useWhiteIcon ? R.drawable.olaicon : R.drawable.olaicon;
    }
}

