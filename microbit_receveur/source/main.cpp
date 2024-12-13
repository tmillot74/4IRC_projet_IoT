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

// Gestionnaire pour les messages reçus
void onData(MicroBitEvent) {
    ManagedString encryptedMessage = uBit.radio.datagram.recv();
    ManagedString decryptedMessage = xorEncryptDecrypt(encryptedMessage, encryptionKey);

    // Débogage : afficher le message reçu (chiffré et déchiffré)
    uBit.serial.printf("Message chiffré reçu : %s\n", encryptedMessage.toCharArray());
    uBit.serial.printf("Message déchiffré : %s\n", decryptedMessage.toCharArray());

    // Envoi d'un ACK chiffré
    ManagedString ack = xorEncryptDecrypt("ACK", encryptionKey);
    uBit.radio.datagram.send(ack);
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
