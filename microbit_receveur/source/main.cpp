#include "MicroBit.h"

MicroBit uBit;

// Clé de chiffrement (doit être identique sur les deux cartes)
const ManagedString encryptionKey = "‡";

// ID de la carte
const int cardId = 1;

// ID de la carte à contacter
const int targetCardId = 0;

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

// Gestionnaire pour les messages reçus
void onData(MicroBitEvent) {
    // ManagedString encryptedMessage = uBit.radio.datagram.recv();

    // Lecture du message reçu
    PacketBuffer buffer = uBit.radio.datagram.recv();
    int senderId = buffer[0];
    int receiverId = buffer[1];
    int messageLength = buffer[2];
    char message[messageLength];
    memcpy(message, buffer.getBytes()+3, messageLength);
    uBit.serial.printf("Message chiffré reçu : %s\r\n", message);


    ManagedString encryptedMessage = ManagedString(message);
    uBit.serial.printf("%d\r\n", senderId);
    uBit.serial.printf("%d\r\n", receiverId);
    uBit.serial.printf("%d\r\n", messageLength);
    // uBit.serial.printf("Message chiffré reçu : %s\r\n", encryptedMessage.toCharArray());

    // Vérifier si le message est destiné à cette carte
    if (receiverId != cardId) {
        return;
    }

    // Vérifier si le message est valide
    if (encryptedMessage.length() == 0) {
        return;
    }

    // Vérifier si la taille du message est valide
    if (encryptedMessage.length() != messageLength-1) {
        return;
    }

    // Déchiffrement du message
    ManagedString decryptedMessage = xorEncryptDecrypt(encryptedMessage, encryptionKey);

    // Débogage : afficher le message reçu (chiffré et déchiffré)
    // uBit.serial.printf("Message chiffré reçu : %s\r\n", encryptedMessage.toCharArray());
    uBit.serial.printf("Message déchiffré : %s\r\n", decryptedMessage.toCharArray());

    // Envoi d'un ACK chiffré
    ManagedString ack = xorEncryptDecrypt("ACK", encryptionKey);
    uBit.radio.datagram.send(ack);
    uBit.serial.printf("ACK envoyé : %s\r\n", ack.toCharArray());
}

int main() {
    uBit.init();
    uBit.radio.enable();
    uBit.serial.setRxBufferSize(254);
    uBit.serial.setTxBufferSize(254);
    uBit.serial.baud(115200);

    // Écoute des événements de réception
    uBit.messageBus.listen(MICROBIT_ID_RADIO, MICROBIT_RADIO_EVT_DATAGRAM, onData);

    // while (1) {
    //     uBit.sleep(1000); // Boucle principale en veille
    // }
    
    release_fiber();
}
