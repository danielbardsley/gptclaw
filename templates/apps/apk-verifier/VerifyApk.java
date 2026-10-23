import com.android.apksig.ApkVerifier;
import java.io.File;
import java.security.MessageDigest;
import java.util.HexFormat;

// Verify signatures, never load or execute APK bytecode. One reviewed development signer.
public final class VerifyApk {
  public static void main(String[] args) throws Exception {
    if (args.length != 1) System.exit(2);
    ApkVerifier.Result result = new ApkVerifier.Builder(new File(args[0]))
        .setMinCheckedPlatformVersion(24).build().verify();
    if (!result.isVerified() || !(result.isVerifiedUsingV2Scheme() || result.isVerifiedUsingV3Scheme())
        || result.getSignerCertificates().size() != 1) System.exit(1);
    byte[] certificate = result.getSignerCertificates().get(0).getEncoded();
    System.out.println(HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(certificate)));
  }
}
