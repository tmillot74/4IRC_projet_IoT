#include "MicroBit.h"

MicroBit uBit;

// Clé de chiffrement (doit être identique sur les deux cartes)
const ManagedString encryptionKey = "9";

// Fonction de chiffrement XOR
ManagedString xorEncryptDecrypt(ManagedString input, ManagedString key) {
    ManagedString result = "";
    int keyLen = key.length();
    for (int i = 0; i < input.length(); i++) {
        char encryptedChar = input.charAt(i) ^ key.charAt(i % keyLen);
        result = result + ManagedString(encryptedChar);
    }
    return result;
}

int main() {
    uBit.init();
    uBit.radio.enable();
    uBit.serial.setRxBufferSize(254);
    uBit.serial.setTxBufferSize(254);
    uBit.serial.baud(115200);

    while (1) {
        // Lecture du port série
        if (uBit.serial.isReadable()) {
            uBit.serial.printf("Entrez un message à envoyer : \n");
            ManagedString plainText = uBit.serial.readUntil('\n');
            uBit.serial.printf("Message à envoyer : %s\n", plainText.toCharArray());

            if (plainText.length() > 0) {
                ManagedString encryptedMessage = xorEncryptDecrypt(plainText, encryptionKey);

                // Attendre l'accusé de réception
                bool ackReceived = false;
                do {
                    uBit.radio.datagram.send(encryptedMessage);
                    ManagedString receivedAck = uBit.radio.datagram.recv();
                    ManagedString decryptedAck = xorEncryptDecrypt(receivedAck, encryptionKey);
                    if (decryptedAck == "ACK") {
                        ackReceived = true;
                        uBit.serial.printf("ACK reçu pour le message : %s\n", plainText.toCharArray());
                    }

                    if (!ackReceived) {
                        uBit.sleep(100);
                        uBit.serial.printf("Aucun ACK reçu pour : %s. Réémission.\n", plainText.toCharArray());
                    }
                } while (!ackReceived);
            }
        }

        uBit.sleep(100); // Anti-rebond
    }

    release_fiber();
}
