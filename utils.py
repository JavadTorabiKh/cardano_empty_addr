from pycardano import PaymentSigningKey, StakeSigningKey, PaymentVerificationKey, StakeVerificationKey, \
    Address, Network, TransactionBuilder, TransactionOutput, BlockFrostChainContext, TransactionInput , \
        TransactionBody
from blockfrost import BlockFrostApi, ApiError, ApiUrls


# Create two enterprise address
# payment_signing_key = PaymentSigningKey.generate()
# payment_verification_key = PaymentVerificationKey.from_signing_key(payment_signing_key)
# payment_signing_key.save("payment.skey")
# payment_verification_key.save("payment.vkey")

# payment_signing_key = PaymentSigningKey.load("payment.skey")

# stake_signing_key = StakeSigningKey.generate()
# stake_verification_key = StakeVerificationKey.from_signing_key(stake_signing_key)

# payment_verification_key = PaymentVerificationKey.load("payment.vkey")
# enterprise_address = Address(payment_part=payment_verification_key.hash(),
#                              network=Network.TESTNET)
# print(enterprise_address)

enterprise_address = 'addr_test1vpffs4ys4nx3eac9nf24vzlgr4cn22udfn2uht5jf69j45q29kplh'
enterprise_address1 = 'addr_test1vqq92q89g8yw2f9jfrvgjeuwd4e04scwc6lwxwneqmx6wts0p35um'




pri_id = 'previewdA5VGB6wweCeCw153KbLOTo4DAgx05DW'


def get_utxo_address(address_from):
    # Connect to Blockfrost
    api = BlockFrostApi(project_id=pri_id, base_url=ApiUrls.preview.value)
    
    try:
        health = api.health()
        print(health)
        utxo_address = api.address_utxos(
            address=address_from)

        return utxo_address

    except ApiError as e:
        print(e)


def get_tx_data(utxo_address):
    tx_hash = []
    for amount in utxo_address:
        tx_hash.append([amount.tx_hash, amount.tx_index])

    return tx_hash



def create_tx_input(tx_data):
    tx_input = []
    for utxo in tx_data:
        tx_id = utxo[0]
        tx_index = utxo[1]
        utxo_input = TransactionInput.from_primitive([tx_id, tx_index])
        tx_input.append(utxo_input)
    
    return tx_input


def create_tx_output(addr_to , all_amount , fee):
    output = TransactionOutput.from_primitive([addr_to, all_amount - fee])
    return output


def create_tx_body(addr_to ,all_amount , fee ):
    utxo_address = get_utxo_address(enterprise_address)
    tx_data = get_tx_data(utxo_address)
    tx_input = create_tx_input(tx_data)
    tx_output = create_tx_output(addr_to , all_amount , fee)
    tx_body = TransactionBody(inputs=tx_input, outputs=[tx_output], fee=fee)
    
    return tx_body





network = Network.TESTNET
context = BlockFrostChainContext(pri_id, network, base_url="https://cardano-preview.blockfrost.io/api")

# Sign and raw Transaction

address_from = enterprise_address1
sk_path = 'payment1.skey'
address_to = enterprise_address

tx_builder = TransactionBuilder(context)
payment_signing_key = PaymentSigningKey.load(sk_path)

# It is required that the entire balance of the address is placed in all_amount 
tx_body = create_tx_body(addr_to=address_to , all_amount=1000000 , fee=170000)

signed_tx = tx_builder.build_and_sign([payment_signing_key], change_address=Address.from_primitive(address_from))
context.submit_tx(signed_tx.to_cbor())
