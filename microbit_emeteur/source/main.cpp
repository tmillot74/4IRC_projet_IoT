#include "MicroBit.h"

MicroBit uBit;

// Clé de chiffrement (doit être identique sur les deux cartes)
const ManagedString encryptionKey = "‡";

// ID de la carte
const int cardId = 0;

// ID de la carte à contacter
const int targetCardId = 1; 

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
            // uBit.serial.printf("Entrez un message à envoyer : \r\n");
            ManagedString plainText = uBit.serial.readUntil('\n');
            // uBit.serial.printf("Message à envoyer : %s\n", plainText.toCharArray());

            // Envoi d'un ACK
            ManagedString ack = "ACK";
            uBit.serial.printf("ACK\r\n");

            if (plainText.length() > 0) {
                // Chiffrement du message
                ManagedString encryptedMessage = xorEncryptDecrypt(plainText, encryptionKey);

                // Création du paquet
                PacketBuffer buffer = PacketBuffer(plainText.length() + 4); // 3 octets pour les ID et la longueur du message et 1 pour le caractère nul
                buffer[0] = cardId; // ID de la carte émettrice
                buffer[1] = targetCardId; // ID de la carte cible
                buffer[2] = plainText.length()+1; // Longueur du message
                memcpy(buffer.getBytes()+3, encryptedMessage.toCharArray(), plainText.length()+1); // Message chiffré

                // Debug 
                // uBit.serial.printf("%d\r\n", buffer[0]);
                // uBit.serial.printf("%d\r\n", buffer[1]);
                // uBit.serial.printf("%d\r\n", buffer[2]);
                // uBit.serial.printf("Message avant chiffrement : %s\r\n", plainText.toCharArray());
                // uBit.serial.printf("Message chiffré envoyé : %s\r\n", encryptedMessage.toCharArray());


                // Attendre l'accusé de réception
                bool ackReceived = false;
                do {
                    uBit.radio.datagram.send(buffer);
                    uBit.sleep(10);
                    ManagedString receivedAck = uBit.radio.datagram.recv();
                    ManagedString decryptedAck = xorEncryptDecrypt(receivedAck, encryptionKey);
                    if (decryptedAck == "ACK") {
                        ackReceived = true;
                        // uBit.serial.printf("ACK reçu pour le message : %s\r\n", plainText.toCharArray());
                    }

                    if (!ackReceived) {
                        uBit.sleep(100);
                        // uBit.serial.printf("Aucun ACK reçu pour : %s. Réémission.\r\n", plainText.toCharArray());
                    }
                } while (!ackReceived);
            }
        }


        uBit.sleep(100); // Anti-rebond
    }

    release_fiber();
}
