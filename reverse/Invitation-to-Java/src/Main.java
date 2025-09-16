import java.awt.Component;
import javax.swing.JOptionPane;
import java.nio.charset.StandardCharsets;

// Base class
abstract class Validator {
    protected byte[] encoded;
    protected byte key;

    public Validator(byte[] encoded, byte key) {
        this.encoded = encoded;
        this.key = key;
    }

    protected String decode() {
        byte[] decoded = new byte[encoded.length];
        for (int i = 0; i < encoded.length; i++) {
            decoded[i] = (byte)(encoded[i] ^ key);
        }
        return new String(decoded, StandardCharsets.UTF_8);
    }

    public abstract boolean validate(String input);
}

// Concrete implementation
class InviteValidator extends Validator {
    public InviteValidator(byte[] encoded, byte key) {
        super(encoded, key);
    }

    @Override
    public boolean validate(String input) {
        String secret = decode();
        return input != null && input.equals(secret);
    }
}

public class Main {
    public static void main(String[] args) {
        // XOR key
        final byte KEY = (byte)0x5A;

        // XOR-encoded flag for: gctf{JavA_1s_v3rY_fuN_BUt_N0t_O0p}
        byte[] encoded = new byte[] {
            61,57,46,60,33,16,59,44,27,5,107,41,5,44,105,40,3,5,60,47,20,5,24,15,46,5,20,106,46,5,21,106,42,39
        };

        // Create validator (polymorphism here, could swap with different validators)
        Validator validator = new InviteValidator(encoded, KEY);

        // Prompt user
        String response = JOptionPane.showInputDialog((Component)null,
                "Enter the flag:", "Crack This Java Language", JOptionPane.QUESTION_MESSAGE);

        if (validator.validate(response)) {
            JOptionPane.showMessageDialog((Component)null,
                    "Correct flag, you are OP at OOP.\nFlag: " + response,
                    "Success!", JOptionPane.INFORMATION_MESSAGE);
        } else {
            JOptionPane.showMessageDialog((Component)null,
                    "Incorrect flag, please try again.", "Failure", JOptionPane.ERROR_MESSAGE);
        }
    }
}
