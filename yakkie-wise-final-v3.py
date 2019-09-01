# -*- coding: utf-8 -*-
import random
import logging

from typing import Union, List

from ask_sdk.standard import StandardSkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.utils import is_request_type, is_intent_name

from ask_sdk_model.services.monetization import (
    EntitledState, PurchasableState, InSkillProductsResponse, Error,
    InSkillProduct)
from ask_sdk_model.interfaces.monetization.v1 import PurchaseResult
from ask_sdk_model import Response, IntentRequest
from ask_sdk_model.interfaces.connections import SendRequestDirective

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Data for the skill

# Static list of facts across 2 categories that serve as
# the free and premium content served by the Skill
all_facts = [
    {
        "type": "fact",
        "fact": "<prosody volume='loud'>Bit</prosody>coin is not tied to any political party, central authority, régime, king, queen, president, dictator, military, or religious leader <audio src='soundbank://soundlibrary/musical/amzn_sfx_church_bell_1x_02'/>, country, alliance, union, social media, or online community, company, corporate group, or anything of the sort. The <prosody volume='loud'>Bit</prosody>coin network simply doesn't care about who wins the elections this year, whose armies have more guns, or what huge corporation decides to split or merge. Whatever political, military, or financial events, the <prosody volume='loud'>Bit</prosody>coin algorithm continues to run 24/7, 365 days a year...<audio src='soundbank://soundlibrary/human/amzn_sfx_large_crowd_cheer_03'/>"
    },
    {
        "type": "fact",
        "fact": "<prosody volume='loud'>Bit</prosody>coin is open for use and exchange for any human being on Earth, regardless of 'his' or 'her': ethnicity, skin colour, religion <audio src='soundbank://soundlibrary/musical/amzn_sfx_church_bell_1x_02'/>, gender, age, sexual preference, background, occupation, education, location, political belief, look, or language. For this reason, whoever you are, wherever you live, whatever your skin colour is, the <prosody volume='loud'>Bit</prosody>coin network, and the underlying protocol, keep on functioning around-the-clock.<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_05'/>"
    },
    {
        "type": "fact",
        "fact": "The supply of <prosody volume='loud'>Bit</prosody>coin is fixed, unlike <prosody volume='loud'>fiat</prosody> currencies, that can be printed at the government's own discretion. <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> There will be a total of 21 million <prosody volume='loud'>Bit</prosody>coin ever created, and there is literally no way to print additional units. This is the way the algorithm was designed. On top of that, there is a fixed <prosody volume='loud'>Bit</prosody>coin generation rate, known by everyone, currently sitting at 12.5 <prosody volume='loud'>Bit</prosody>coin, once every 10 minutes. Scarcity, transparency, and predictability, are some of the key attributes that an ideal currency should have, and Bitcoin meets these criteria.<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_04'/>"
    },
    {
        "type": "fact",
        "fact": '''Each <prosody volume='loud'>Bit</prosody>coin is divisible up to the 8th decimal place, meaning it can be broken down into 100,000,000 sub-units, called Satoshis, or simply <prosody volume='loud'><phoneme alphabet='ipa' ph="s'æts">sats</phoneme></prosody>. The name of this sub-unit, comes from the anonymous creator of <prosody volume='loud'>Bit</prosody>coin, Satoshi Nakamoto. <audio src='soundbank://soundlibrary/foley/amzn_sfx_glasses_clink_03'/> Since 2009, many have tried, and failed, to identify the person, or the group of people behind this pseudonym. Maybe we will never solve this mistery... Maybe we don't need to.<audio src='soundbank://soundlibrary/human/amzn_sfx_large_crowd_cheer_03'/>'''
    },
    {
        "type": "fact",
        "fact": "New <prosody volume='loud'>Bit</prosody>coin is generated every 10 minutes, through a process called <prosody rate='slow'>mining</prosody> <audio src='soundbank://soundlibrary/foley/amzn_sfx_silverware_clank_03'/>, and, until the year 2020, there are 12.5 <prosody volume='loud'>Bit</prosody>coin generated with each 10-minutes block. Starting 2020, this amount drops to 6.25 <prosody volume='loud'>Bit</prosody>coin, mined every 10 minutes. This event, called 'the <prosody volume='loud'>Bit</prosody>coin <prosody rate='slow'>halvening'</prosody>, occurs once every 210,000 blocks, or approximately every 4 years, and its purpose is to reduce the block reward each time. Historically, the <prosody volume='loud'>Bit</prosody>coin halvening has a certain degree of influence over the price of <prosody volume='loud'>Bit</prosody>coin, but that's definitely not set in stone, so be cautious if you're planning on speculating.<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_05'/>"
    },
    {
        "type": "fact",
        "fact": "There are currently 12.5 <prosody volume='loud'>Bit</prosody>coin, generated once every 10 minutes, through a process, also known as <prosody rate='slow'>mining</prosody> <audio src='soundbank://soundlibrary/foley/amzn_sfx_silverware_clank_03'/> Since the <prosody volume='loud'>Bit</prosody>coin generation rate is public, and forever ingrained in its algorithm, we know that the last <prosody volume='loud'>Bit</prosody>coin will be mined in the year 2140. Through this algorithm, we can know exactly how many <prosody volume='loud'>Bit</prosody>coin will be in circulation tomorrow, next week, next year, or in the year 2058. Try that with any fiat currency, such as the dollar, or the euro, to feel the taste of disappointment.<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_04'/>"
    },
    {
        "type": "fact",
        "fact": "<prosody volume='loud'>Bit</prosody>coin does not abide to any central management, nor does it have a central point of failure. It has no headquarters, no board of directors, no employees, no buildings, no call center, and no <prosody volume='loud'>press</prosody> center. <audio src='soundbank://soundlibrary/office/amzn_sfx_typing_typewriter_01'/> This doesn't mean it has no rules. However, these rules are agreed upon by the vast majority of network participants, and transactions are undeniably validated through a consensus algorithm, called Proof-of-Work, which involves processing power, electrical energy, and also human resources and logistics, distributed across many geographical regions, to keep the network functional, trustworthy, and highly secured.<audio src='soundbank://soundlibrary/human/amzn_sfx_large_crowd_cheer_03'/>"
    },
    {
        "type": "fact",
        "fact": "<prosody volume='loud'>Bit</prosody>coin is meant to be a global currency, as well as a store of value, regardless of hemisphere, continent, country, state, or region. <audio src='soundbank://soundlibrary/foley/amzn_sfx_glasses_clink_02'/> The <prosody volume='loud'>Bit</prosody>coin network is distributed across a wide range of countries and all continents, and the free exchange of <prosody volume='loud'>Bit</prosody>coin cannot be restricted, neither between the borders of a state, nor <prosody volume='loud'>cross</prosody>-border. This feature of <prosody volume='loud'>Bit</prosody>coin, makes it the best international, peer-to-peer, censorship-resistant, payments settlement system currently in existence.<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_05'/>"
    },
    {
        "type": "fact",
        "fact": "Because of its decentralized nature, <prosody volume='loud'>Bit</prosody>coin cannot, and <prosody volume='x-loud'>will</prosody> not be censored, in any way, shape, or form. Nor will it be shutdown. Indeed, governments, <audio src='soundbank://soundlibrary/human/amzn_sfx_clear_throat_ahem_01'/> have tried to ban, outlaw, or forbid any operations involving cryptocurrencies, such as <prosody volume='loud'>Bit</prosody>coin, Ethereum, <prosody volume='loud'>Lite</prosody>coin, and others, but soon came to the conclusion that a paper decree has nothing to do with the ability to technically deny access to the <prosody volume='loud'>Bit</prosody>coin network for its citizens. So, good luck to those trying to prohibit or suppress the free exchange of <prosody volume='loud'>Bit</prosody>coin.<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_04'/>"
    },
    {
        "type": "fact",
        "fact": "Since one of the <prosody volume='loud'>key</prosody> attributes of <prosody volume='loud'>Bit</prosody>coin is its scarcity and limited supply, with no central bank to hit the Print button, and flood the market with new money once in a while, this incurs the exact opposite of inflation. That is called <prosody volume='loud'>de</prosody>flation. Given its fixed supply, and a growing demand for a currency with such characteristics, the price and purchasing power of <prosody volume='loud'>Bit</prosody>coin have no way to go but up. <prosody volume='loud'>Bit</prosody>coin's recognition and popularity have been on a general uptrend over the past years, and once the fears, lies, and manipulation about <prosody volume='loud'>Bit</prosody>coin will have faded away, the masses will pay more attention to this emerging technology and market.<audio src='soundbank://soundlibrary/human/amzn_sfx_large_crowd_cheer_03'/>"
    },
    {
        "type": "fact",
        "fact": "Fungibility is the property of a good, or a commodity, whose individual units are essentially interchangeable. So, just like a $20 bill is equally valuable to another $20 bill, <prosody volume='loud'>Bit</prosody>coin is also fungible, meaning that 1 <prosody volume='loud'>Bit</prosody>coin is of equal value to another 1 <prosody volume='loud'>Bit</prosody>coin. If this still sounds a bit weird, think of other goods that are not fungible. Such as beef, or chicken meat, for instance. <audio src='soundbank://soundlibrary/animals/amzn_sfx_chicken_cluck_01'/> In this case, 1 pound of meat, may have a different value than another pound of meat, based on breed, origin, or dietary. Therefore, fungibility,, Checked.<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_05'/>"
    },
    {
        "type": "fact",
        "fact": "In order for a <prosody volume='loud'>Bit</prosody>coin transaction to be settled, there is no need for a third party, such as a bank, or an alternative payment system, to approve, process, and complete the transaction. This way, especially with cross-border payments, you're avoiding three drawbacks that traditional payment systems possess: <audio src='soundbank://soundlibrary/human/amzn_sfx_drinking_slurp_01'/>... 1. high fees, sometimes up to 10% of the amount you send. 2. disadvantageous payment processing times, of about 3 to 5 business days for instance. And 3. No privacy, all of your transactions being stored somewhere in a centralized database server, that is prone to prying eyes, and hackers. That's why, on top of being completely decentralized and censorship-resistant, <prosody volume='loud'>Bit</prosody>coin is considered an amazing peer-to-peer payments system.<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_04'/>"
    },
    {
        "type": "fact",
        "fact": "<prosody volume='loud'>Bit</prosody>coin is easily portable, as opposed to cash or gold, whether you're going out to grab lunch, or crossing the border to a neighbouring country. <audio src='soundbank://soundlibrary/transportation/amzn_sfx_airplane_takeoff_whoosh_01'/> It's pretty effortless to have access to your funds at any time. Moreover, when creating your own <prosody volume='loud'>Bit</prosody>coin wallet, you will be granted a <prosody volume='loud'>seed</prosody>, which is actually a list of 12, 18, or 24 random words, that represents your <prosody volume='loud'>private</prosody> key. You can use this seed at any time to re-create your wallet, and recover your coins, in case your smartphone, laptop, or hardware wallet breaks or gets lost. Remembering those words in the <prosody volume='loud'>specific</prosody> order they were generated by your wallet, is yet another method of carrying your <prosody volume='loud'>Bit</prosody>coin stash wherever you go. Your brain is the safest wallet. Just be careful not to trip and hit your head.<audio src='soundbank://soundlibrary/human/amzn_sfx_large_crowd_cheer_03'/>"
    },
    {
        "type": "fact",
        "fact": '''Each <prosody volume='loud'>Bit</prosody>coin wallet has its own address, namely a long string of random letters and numbers. <audio src='soundbank://soundlibrary/office/amzn_sfx_typing_medium_02'/> Think of this string as your own bank account number, or <phoneme alphabet='ipa' ph="'aɪ">I</phoneme>-BAN. This is the address you share with others to receive <prosody volume='loud'>Bit</prosody>coin, and it is distinct from your <prosody volume='loud'>Private</prosody> key, which is the key used to access your funds, and sign transactions in order to send <prosody volume='loud'>Bit</prosody>coin. So, keep in mind that you can share the public key or address with others, but you should 'always' keep your <prosody volume='loud'>Private</prosody> key, secret. Your wallet address is all you need, in order to ask someone to send you some <prosody volume='loud'>Bit</prosody>coin. No name, home address, ID, passport, nothing of the sort. Privacy at its best.<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_05'/>'''
    },
    {
        "type": "fact",
        "fact": "Being an electronic record, and also a unit of account, in a distributed, decentralized, immutable ledger, <prosody volume='loud'>Bit</prosody>coin cannot be physically broken, <audio src='soundbank://soundlibrary/foley/amzn_sfx_silverware_clank_03'/>, burnt, stained, wetted, bent, oxidized, like cash is... or melted, and contaminated with other substances, as in the case of gold, silver, or platinum. It has no weight, no volume, no texture, and no density. <prosody volume='loud'>Bit</prosody>coin is as durable as the blockchain technology, and the supporting distributed network it <prosody volume='loud'>relies</prosody> on.<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_04'/>"
    },
    {
        "type": "fact",
        "fact": "The <prosody volume='loud'>Bit</prosody>coin ledger is maintained, verified, and stored on a global network of computers, where each computer is called a <prosody volume='loud' rate='slow'>node</prosody>. There are currently thousands of <prosody volume='loud'>Bit</prosody>coin <prosody volume='loud' rate='slow'>nodes</prosody> all around the world, and they all contribute to the verification, consensus, and decentralization of the <prosody volume='loud'>Bit</prosody>coin blockchain. Attacking, <audio src='soundbank://soundlibrary/battle/amzn_sfx_army_march_clank_7x_01'/>, disrupting, or destroying a network so distributed, so global, so computationally robust, backed by a <emphasis level='strong'>huge</emphasis> amount of processing power, would be a daunting task for anyone. <prosody volume='loud'>This</prosody> is the reason why <prosody volume='loud'>Bit</prosody>coin continues to be unhackable since 2009, and, the more nodes get spawned, the <prosody volume='loud'>harder</prosody> it gets for any entity to threaten <prosody volume='loud'>Bit</prosody>coin's security and stability. You can say that the <prosody volume='loud'>Bit</prosody>coin network, is currently the most secure network in the world.<audio src='soundbank://soundlibrary/human/amzn_sfx_large_crowd_cheer_03'/>"
    },
    {
        "type": "fact",
        "fact": "Unlike cash, or precious metals, <prosody volume='loud'>Bit</prosody>coin cannot be forged, thus there's no notion of 'fake <prosody volume='loud'>Bit</prosody>coin'. <audio src='soundbank://soundlibrary/foley/amzn_sfx_glasses_clink_02'/> Basically, the Blockchain is a distributed ledger, containing all the <prosody volume='loud'>Bit</prosody>coin transactions that ever took place since its inception, in 2009. Transactions are grouped into blocks, and upon validation, each block is added to the chain, and linked to the previous block, through the result of a cryptographic function, called hash. This way, the validity of each block of transactions can be traced back to even the first block ever created, which is called the <prosody rate='slow'>genesis</prosody> block.<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_05'/>"
    },
    {
        "type": "fact",
        "fact": "In order for an attacker to forge <prosody volume='loud'>Bit</prosody>coin, he or she would have to: a) have 51% of <prosody volume='loud'>Bit</prosody>coin's total network processing power, which would be <prosody volume='loud'>extremely</prosody> hard to fund and build, even by the most sophisticated nation-state, <audio src='soundbank://soundlibrary/human/amzn_sfx_cough_01'/> and b) alter the history of the blockchain, meaning he or she would have to alter a block that was already mined and validated in the past, and also re-mine all subsequent blocks, thus reverting all the transactions inside the chosen block, as well as all subsequent transactions to date, which, again, would imply <prosody volume='x-loud'>massive</prosody> amounts of resources. Both of these scenarios are <prosody volume='loud'>highly</prosody> impractical, as <prosody volume='loud'>Bit</prosody>coin's network continues to grow.<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_04'/>"
    },
    {
        "type": "fact",
        "fact": '''The Blockchain, is an open, transparent, public ledger of transactions. Each and every transaction ever made with <prosody volume='loud'>Bit</prosody>coin, is public, and free for anyone to see, with no effort at all. As soon as a transaction has been confirmed, and added to a block, and that block appended to the Blockchain, it is part of the permanent record, and cannot be ever reverted. <audio src='soundbank://soundlibrary/foley/amzn_sfx_glasses_clink_02'/> Another reason why <prosody volume='loud'>Bit</prosody>coin is considered as transparent as it can be, is because its code is 100% open-source, and some of the most talented developers all over the world, are constantly contributing to its development on <phoneme alphabet='ipa' ph="g'Ithʌb">github</phoneme>.<audio src='soundbank://soundlibrary/human/amzn_sfx_large_crowd_cheer_03'/>'''
    },
    {
        "type": "fact",
        "fact": "The <prosody volume='loud'>Bit</prosody>coin network is continuously up and running, validating and recording transactions, generating new <prosody volume='loud'>Bit</prosody>coin, and constantly improving the software and its performance, with the help of a huge community of developers all over the world. <audio src='soundbank://soundlibrary/foley/amzn_sfx_glasses_clink_01'/> Moreover, you can buy and sell <prosody volume='loud'>Bit</prosody>coin, and any other cryptocurrencies, 24 hours a day, 7 days a week, 365 days a year, since cryptocurrency exchanges never sleep or go on a break, unlike traditional banks and stock market exchanges do.<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_05'/>"
    },
    {
        "type": "legend",
        "fact": "Some people say that <prosody volume='loud'>Bit</prosody>coin is created out of thin air. <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> Actually, that is incorrect. <prosody volume='loud'>Bit</prosody>coin is generated once every approximately 10 minutes, through a process called mining. I should emphasize the fact, that the mining process itself does not have <prosody volume='loud'>Bit</prosody>coin creation as its primary purpose. Instead, the main roles of mining are securing the blockchain, and reaching network-wide consensus, without the need of a central authority. The miners are incentivized to participate in this process, by earning two types of rewards: 1. new <prosody volume='loud'>Bit</prosody>coin, created with each new block of transactions, and 2. transaction fees, associated with all the transactions inside that block. <prosody volume='loud'>Bit</prosody>coin mining is performed in specialized buildings, with immense cooling capabilities, significant maintenance costs, and human resources to operate, monitor, and fix the devices, on a 24/7 work schedule. So, not quite out of <prosody volume='loud'>thin air</prosody>, isn't it? <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_04'/>"
    },
    {
        "type": "legend",
        "fact": "Some people say that <prosody volume='loud'>Bit</prosody>coin is not a means of exchange. <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> Before diving into whether <prosody volume='loud'>Bit</prosody>coin has any utility or not, let's think about the utility of money, in general. Basically, in order to be considered a functional currency, money has to have three main functions: first... means of exchange, secondly... store of value, and finally... unit of account. Means of exchange, refers to the ability of exchanging money for goods and services. Although not yet widely adopted, <prosody volume='loud'>Bit</prosody>coin payments are already accepted in thousands of venues, and on websites across the world. Moreover, the utility of <prosody volume='loud'>Bit</prosody>coin is massively enhanced by the fact that it is a peer-to-peer payment method, meaning no one else, besides you and the business accepting your payment, is involved in the transaction, which leads to much lower fees, a higher level of privacy, and faster confirmation times for your payment. That's gonna be a huge hit for your bank, trust me! But hey, who loves banks anyway? I know <prosody volume='x-loud'>I</prosody> don't!<audio src='soundbank://soundlibrary/human/amzn_sfx_large_crowd_cheer_03'/>"
    },
    {
        "type": "legend",
        "fact": "Some people say that <prosody volume='loud'>Bit</prosody>coin is not a store of value, because of its price volatility. <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> Before diving into whether <prosody volume='loud'>Bit</prosody>coin has any utility or not, let's think about the utility of money, generally speaking. Basically, in order to be considered a functional currency, money has to have three main functions: 1. means of exchange, 2. store of value, and 3. unit of account. Store of value, means that the money you put aside, maintain their value over time, and are not perishable. For instance, you cannot store value in apples for the next 20 years. Invoking volatility as a reason why <prosody volume='loud'>Bit</prosody>coin is not a suitable store of value, is simply incorrect. Comparing <prosody volume='loud'>Bit</prosody>coin to gold, by considering the lifetime of each of these assets, and taking a quick look at the price chart of both of them, side by side, the degree of volatility is actually quite similar. However, again, assuming proportional time scales, <prosody volume='loud'>Bit</prosody>coin definitely stores considerably more value, than its shiny counterpart, as proven by its price evolution from one year to another. So, next time you hear your <prosody volume='loud'>Bit</prosody>coin-skeptic friend bragging about his gold stack, ask him about his gold portfolio, between 2012 and 2016. Then, watch his face turn blue.<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_05'/>"
    },
    {
        "type": "legend",
        "fact": "Some people say that <prosody volume='loud'>Bit</prosody>coin cannot be used as an unit of account. <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> Before diving into whether <prosody volume='loud'>Bit</prosody>coin has any utility or not, let's think about the utility of money, in a broad sense. Basically, in order to be considered a functional currency, money has to have three main functions: First... means of exchange, secondly... store of value, and last, but not least, unit of account. Using money as a unit of account, means that you are able to use it to quantify goods and services. For instance, 1 coffee, in exchange for 3 US dollars. <prosody volume='loud'>Bit</prosody>coin is definitely a unit of account, since you can price goods and services in BTC. There are online services, digital products, and even apartments or cars, priced in <prosody volume='loud'>Bit</prosody>coin, and the number of merchants accepting <prosody volume='loud'>Bit</prosody>coin is continuously increasing. Don't trust me? Check out real estate agencies in Dubai, selling beautiful apartments in exchange for <prosody volume='loud'>Bit</prosody>coin. Of course, the prices are pretty high, so make sure your wallet is in <prosody volume='loud'>top</prosody> shape!<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_04'/>"
    },
    {
        "type": "legend",
        "fact": '''<prosody rate='slow'><phoneme alphabet="ipa" ph="n'eɪseɪɚs">Naysayers</phoneme></prosody> claim that <prosody volume='loud'>Bit</prosody>coin is nothing more than magic Internet money. <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> <prosody volume='loud'>Bit</prosody>coin represents a complex technological environment, comprising of thousands of advanced computers and users around the world, a secure and immutable public ledger, a mechanism to implement decentralization, and achieve consensus, based on vast computer resources, dedicated to validating and recording transactions, and a clear set of rules, agreed by the overwhelming majority of users in the network, not by a central entity. <prosody volume='loud'>Bit</prosody>coin is a peer-to-peer electronic payment system, that uses the Internet as its transport layer, that excludes third parties, and eliminates transaction delays and unreasonably high fees. Unlike traditional currencies, <prosody volume='loud'>Bit</prosody>coin is deflationary, unforgeable, borderless, open to everyone, and censorship-resistant. There is no entity that can print additional <prosody volume='loud'>Bit</prosody>coin at will, like central banks do. Also, there is no forger who can falsify <prosody volume='loud'>Bit</prosody>coin, no government that can ban its citizens from using <prosody volume='loud'>Bit</prosody>coin, as well as no hacker who has been able to disrupt or destroy the <prosody volume='loud'>Bit</prosody>coin network. <prosody volume='loud' rate='x-slow' pitch='high'>There's</prosody> your magic!<audio src='soundbank://soundlibrary/human/amzn_sfx_large_crowd_cheer_03'/>'''
    },
    {
        "type": "legend",
        "fact": "<prosody volume='loud'>Bit</prosody>coin opponents say that it is just a silly digital equivalent of cash <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/>, used by teenagers and anarchists, to buy things on the Internet. However, <prosody volume='loud'>Bit</prosody>coin is way more than a form of electronic cash. It is an ecosystem of millions of developers, engineers and users. It's a network of computers, outperforming the world's largest supercomputers by several orders of magnitude. It's a tool for financial and social inclusion, for several billion people not having access to any kind of financial services, people who are paying up to 10% fees to send money back to their families, in less fortunate countries. It's an emerging market, with a capitalization of hundreds of billions of US dollars, estimated to grow into the trillions. I don't consider this to be silly.<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_05'/>"
    },
    {
        "type": "legend",
        "fact": "In some circumstances, some people claimed that <prosody volume='loud'>Bit</prosody>coin transactions were slow. <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> That was partially true, at some point during <prosody volume='loud'>Bit</prosody>coin's evolution, especially throughout the bull market of 2017. By default, <prosody volume='loud'>Bit</prosody>coin is able to process anywhere between 3 and 7 transactions per second, with a median confirmation time of about 7 to 10 minutes, and a required number of 6 confirmations for the transfer to be considered complete. So, a total of about 45 minutes to an hour, to settle everything. However, the most recent development in <prosody volume='loud'>Bit</prosody>coin is the Lightning Network, which is a layer 2 scaling solution on top of the <prosody volume='loud'>Bit</prosody>coin protocol, that enables the creation of off-chain, bidirectional payment channels between two parties, resulting in the ability to easily perform thousands of micropayments, with extremely low fees, and almost instantly. This means that your transaction when buying a cup of coffee, doesn't need to be mined, and added to the blockchain. Instead, the Lightning Network enables you to open a payment channel with your favourite coffee shop, and settle your microtransactions with this particular merchant, off-chain. Later on, when you decide to close the channel, the virtual balance sheet between you and the coffee shop is settled, and the final result is the one to be recorded as a transaction on the <prosody volume='loud'>Bit</prosody>coin blockchain. Pretty cool, I think!<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_04'/>"
    },
    {
        "type": "legend",
        "fact": "People not familiar with the Lightning Network, one of the most recent developments in the <prosody volume='loud'>Bit</prosody>coin world, may say that <prosody volume='loud'>Bit</prosody>coin is too expensive for working with micropayments. <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> Here's an example that Andreas Antonopoulos gave in one of his videos. Imagine you rent a car for a week, and you get an insurance for this period of time. Instead of paying the insurer for the entire week, of which you spend most of the time sleeping, walking or working, you are able to pay per second spent actually driving. As soon as you get out of the car, your insurance is paused, and you are not charged. As soon as you get back into the car, the timer is un-paused, and you're getting charged again. Of course, micropayments this size would not be possible with an on-chain solution, because the fee you would need to pay for each microtransaction to be validated by miners, would surpass the transaction value itself. But, with the Lightning Network, such micropayments are not an issue anymore, since, according to the documentation, Lightning enables one to send funds down to 0.00000001 <prosody volume='loud'>Bit</prosody>coin. Can't get more micro than <prosody volume='loud'>that</prosody>!<audio src='soundbank://soundlibrary/human/amzn_sfx_large_crowd_cheer_03'/>"
    },
    {
        "type": "legend",
        "fact": '''I've heard some people, babbling about how the users of the <prosody volume='loud'>Bit</prosody>coin Lightning Network, should worry about the fees that they'll have to pay for each of their payments, and how this might not be too optimal. <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> Let's get one thing straight. You, as a Lightning Network user, won't have to worry about which path in the network will incur the lowest fees, to get your payment through. This is going to be automatically handled by the client software, namely your wallet, that will analyze the options, and select the most cost-effective payment path, on your behalf. Given that the Lightning Network technology matures at an exponential rate, soon you won't have to deal with nothing more than just choosing Dave, or Carol, in your wallet's contact list, and pressing the <prosody volume='loud'>Send</prosody> button, to instantly pay the 50 cents, 5 dollars, or 50 dollars that you owe, with minimal fees, even on a Sunday afternoon. Let that <prosody volume='loud' rate='slow'>sink <phoneme alphabet="ipa" ph="'in">in</phoneme></prosody> for a moment.<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_05'/>'''
    },
    {
        "type": "legend",
        "fact": '''Price volatility, maybe one of the top 3 reasons invoked by <prosody rate='slow'><phoneme alphabet="ipa" ph="n'eɪseɪɚs">Naysayers</phoneme></prosody>, when it comes to <prosody volume='loud'>Bit</prosody>coin and cryptocurrencies. <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> The first question that comes to my mind is: too volatile, compared to what? Indeed, the price of <prosody volume='loud'>Bit</prosody>coin has fluctuated quite significantly since its inception, with several bull and bear cycles. Of course, most people tend to look only at the most recent bear market, which started in January 2018, because that's when most people got burned. But, let's make this very clear, although the truth might be painful to hear. It's not <prosody volume='loud'>Bit</prosody>coin's price evolution that made people lose money in recent times, but <prosody volume='loud'>greed</prosody>, and lack of any financial knowledge and common sense. In December of 2017, people were buying <prosody volume='loud'>Bit</prosody>coin and other cryptocurrencies like crazy, just because the next person was doing the same thing, and mainstream media was pumping this mania to extreme levels. Finally, if you take a look at the history of gold and silver, WTI and Brent crude oil, and the SnP 500 stock index, it's very easy to notice that every market goes through bull and bear cycles, and great volatility, when speculators are either shorting or going long on the price of the asset, whatever that asset may <prosody volume='loud'>be</prosody>. Stating that <prosody volume='loud'>Bit</prosody>coin is way more volatile and unstable than gold or oil, is pretty unfair, because you're ignoring an important factor: time. Comparing the market fluctuations of several-decades-old commodities and indexes, with just a decade-year-old asset like <prosody volume='loud'>Bit</prosody>coin, is not the wisest approach. Considering <prosody rate='slow'><phoneme alphabet="ipa" ph="n'eɪseɪɚs">Naysayers</phoneme></prosody> wise is not a good idea, either. So, trust the facts, not the words!<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_04'/>'''
    },
    {
        "type": "legend",
        "fact": '''<prosody volume='loud'>Bit</prosody>coin mining is too centralized! <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> I've heard this a lot, and I won't argue whether or not the current distribution or concentration of mining pools is too centralized. Instead, what everyone must understand is that decentralization is not a binary concept, a matter of 'yes or no', nor 'black or white'. Instead, decentralization should be regarded as a scale, where a particular system or network is more centralized than <prosody volume='loud'>another</prosody> entity with a similar role. Agreeing that there is no such thing as perfectly centralized, or perfectly <phoneme alphabet="ipa" ph="'di">de</phoneme>centralized, we must view this topic from a sligthly different, more flexible angle. That being said, when comparing the <prosody volume='loud'>Bit</prosody>coin network, having a relatively small number of mining pools, but a high degree of neutrality, privacy, security and resistance to censorship, with another system like a central bank, which is dictating the monetary supply, or a <prosody volume='loud'>private</prosody> bank, which owns all of your money and plays around with it to generate profit, or a payment processing company, holding records of all your transaction history, claiming that <prosody volume='loud'>Bit</prosody>coin is somehow too centralized, is kind of a stretch.<audio src='soundbank://soundlibrary/human/amzn_sfx_large_crowd_cheer_03'/>'''
    },
    {
        "type": "legend",
        "fact": "Maybe the number <prosody volume='loud'>one</prosody> argument against <prosody volume='loud'>Bit</prosody>coin, is that it consumes way too much energy. <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> The question that comes to mind immediately, - for those of us who <prosody volume='loud'>use</prosody> their minds, - is: compared to what? Let's imagine for a moment that <prosody volume='loud'>Bit</prosody>coin takes over <prosody volume='loud'>all</prosody> other traditional payment systems, and becomes a worldwide currency. Bear with me here, please! This would mean that all or most private banks and payment processors go out of business. I know this seems like a far-fetched example, but hold on for one more second. What would that mean, in terms of energy consumption, and carbon footprint? Well, there wouldn't be any more 50-storey bank headquarters all around the world. No fancy, flashy, electricity-hungry office buildings in every major city across 6 continents, no bank branch office at every street corner, no thousands of other payment processing companies and intermediaries, with subsidiaries all over the world, all together consuming way more than <prosody volume='loud'>Bit</prosody>coin's miners. How many households in the United States could be powered by this overwhelmingly demanding industry? Dare to do the math? Ridiculous argument against <prosody volume='loud'>Bit</prosody>coin. It really is!<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_05'/>"
    },
    {
        "type": "legend",
        "fact": "I absolutely love people condemning the so-called 'large energy consumption', and the associated carbon footprint of the <prosody volume='loud'>Bit</prosody>coin network. <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> As a comparison, let's think about the current banking and payment processing systems, along with the millions of employees using their cars each and every day to get to work, back and forth, spending hours in heavy traffic. Isn't that a gigantic CO2 generator when combined? Let's take a moment, and think about one of the largest global payment processing companies, having offices all around the world. I won't name any names. Judging from their website's career page, this company alone has one or several offices in: India, China, USA, Ukraine, Sri Lanka, Singapore, UK, France, Malaysia, Morocco, Vietnam, Brazil, Mexico, Panama, the United Arab Emirates, Canada, The Phillipines, Côte d'Ivoire, South Africa, Saudi Arabia, Kenya, Hong Kong, Pakistan, Serbia, Australia, Costa Rica, Colombia, Russia, Indonesia, Argentina, Peru, Dominican Republic, Japan, Thailand, South Korea, and Taiwan. Had enough? Now, multiply that by the number of large banks and related financial corporations. Are you still positive that the <prosody volume='loud'>Bit</prosody>coin network is the most environmentally-unfriendly payment system, consuming way too much energy, and polluting the planet? A piece of advice: whenever you hear 'too much', always ask yourself: 'Compared to what?'<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_04'/>"
    },
    {
        "type": "legend",
        "fact": "<prosody volume='loud'>Bit</prosody>coin is just a bubble. <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> How many times have you heard that? Can we argue this? Well, honestly, no! History tells us that <prosody volume='loud'>Bit</prosody>coin had quite a lot of bubbles over the years, so, people grumbling that '<prosody volume='loud'>Bit</prosody>coin is a bubble', and acting like Christopher Columbus discovering the Americas, doesn't make them look smart or visionary, it only makes everyone else bored to death. Now, by analyzing recent history, we can firmly agree that the <prosody volume='loud'>Bit</prosody>coin and cryptocurrency market is not only a bubble, but a collection of bubbles, starting in 2012 and peaking in 2017 and 2018. However, comparing the cryptocurrency market crash of 2018, with the Dot-Com bubble in the 1990s and early 2000s, is only partially accurate, since at the time the Dot-Com bubble was inflating and preparing to burst, the companies in the NASDAQ index were being traded on a fully regulated and supervised market, mostly by large investment funds and banks, and so-called trading professionals and brokers. On the other hand, cryptocurrencies are being traded mostly by young, less experienced investors, seeking profits, involvement in an innovative field, or freedom from traditional, corrupt systems, like governments and banks. Why is this distinction so important? Because having such a huge stock market crash in the early 2000s, with a load of stocks and IPO's being heavily backed and pumped by professional, institutional investors, is light-years more disappointing and blamable, than a cryptocurrency market bubble led mostly by the greed and fear of young, enthusiastic investors. Who's the bubble boy now?<audio src='soundbank://soundlibrary/human/amzn_sfx_large_crowd_cheer_03'/>"
    },
    {
        "type": "legend",
        "fact": "There are definitely quite a few enthusiastic defenders of the US dollar against <prosody volume='loud'>Bit</prosody>coin, stating that <prosody volume='loud'>Bit</prosody>coin is worthless, when compared to the dollar. <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> Before stating the obvious arguments why <prosody volume='loud'>Bit</prosody>coin <prosody volume='loud'>does</prosody> have value, let's zoom out a bit, and think about the concept of 'value', or 'intrinsic value'. Also, let's ask ourselves a couple of questions, such as... 'What's the intrinsic value of a $100 bill?', or 'What's the intrinsic value of gold?', or 'What's the intrinsic value of oil?'. Intrinsic value, is not an attribute or a virtue, that Mother Nature, or the Universe, or God, assigns to a particular asset by default, thus classifying every thing on the face of the Earth as having or not having value. The value of a certain asset, is given by a community of people, agreeing upon whether to use that asset to get something in return, or fulfill a need, in a particular environment, and over a period of time. The US dollar was decoupled from gold by Richard Nixon in 1971, during what is now known as the Nixon shock. So, from decades ago, the US dollar bill is nothing more than a fancy piece of paper, with various symbols of trust, such as the face of Benjamin Franklin, the seals of the US Federal Reserve and Treasury, signatures of both the Secretary of the Treasury and the US Treasurer, and various other images and security elements. With the possibility of being printed at will, thus increasing the money supply overnight and creating inflation, the market value of the US dollar decreases over time, leading to less purchasing power, but its actual intrinsic value, is physically equal to that of the paper it's being printed on. Truth hurts, I know!<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_05'/>"
    },
    {
        "type": "legend",
        "fact": "<prosody volume='loud'>Bit</prosody>coin has no intrinsic value whatsoever, as <prosody volume='loud'>gold</prosody> does! <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> Have you heard this legend? Or, should I say.. low level manipulation? Let's use logic, and get back to the basics. What is the intrinsic value of gold? Why would gold have any intrinsic value by itself? Even if it's being used for thousands of years as a symbol of wealth and social status, and for building electronic components in recent times, gold does <prosody volume='loud'>not</prosody> have an universal intrinsic value. Notice I mentioned the phrase... 'it's being used'. Millions of years ago, Homo Habilis and Homo Erectus, would not have been too excited about a bar of gold, lying around next to a tree. Why?! Because it would've been of no use to him. He didn't care about social status too much, nor did he had a smartphone with gold circuits inside. It's all about community and usability. The same logic can be further extended to oil, for instance. If there wouldn't be any industry or automobiles, no one would need oil, hence its universal intrinsic value is, well, zero. However, since in today's world, oil is needed by various communities and industries, oil <prosody volume='loud'>does</prosody> have a market value. What about water? If the Earth would've been uninhabited, who would need water to quench their thirst? Is there an intrinsic value to water? No, it isn't. Instead, its value is objectified by our presence. Again, community, and use case. Now, a large community of people, who value decentralization, censorship-resistance, independence from banks and abusive governments, peer-to-peer value exchange, non-discrimination, security, and deflationary currencies, has decided that <prosody volume='loud'>Bit</prosody>coin is useful. Deal with it!<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_04'/>"
    },
    {
        "type": "legend",
        "fact": "I adore people ignorantly asking... What does <prosody volume='loud'>Bit</prosody>coin have, that regular, fiat currencies don't? <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> Well, let me provide you with a couple of examples. First of all, unlike your national currency, <prosody volume='loud'>Bit</prosody>coin has scarcity and deflation. There are 21,000,000 <prosody volume='loud'>Bit</prosody>coin ever to be created, with an easily verifiable and mathematically predictible generation rate. The exact number of <prosody volume='loud'>Bit</prosody>coin in circulation at any time, can be verified online. On the other hand, no one knows how many US dollars, or euros, are there in circulation at any moment, and the creation of new money is highly impredictable, and alarmingly opaque for the general public. As a result of its scarcity and growing demand, <prosody volume='loud'>Bit</prosody>coin's deflation is an attribute that all fiat currencies dream of, but fail to achieve. The second argument would be openness, and lack of borders. <prosody volume='loud'>Bit</prosody>coin is open for use and exchange for any human being on Earth, regardless of ethnicity, skin colour, religion, gender, age, sexual preference, political preference, or credit score. The <prosody volume='loud'>Bit</prosody>coin network is distributed across a wide range of countries, and on all continents, and the exchange of <prosody volume='loud'>Bit</prosody>coin cannot be restricted neither between the borders of a state, nor cross-border. So, how's that compared to your little own national coin? I think <prosody volume='loud'>Bit</prosody>coin is light-years ahead.<audio src='soundbank://soundlibrary/human/amzn_sfx_large_crowd_cheer_03'/>"
    },
    {
        "type": "legend",
        "fact": '''What's so special about <prosody volume='loud'>Bit</prosody>coin, and why is it so much better than the plain old fiat currencies? <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> I get this question a lot, and although there are quite a few reasons why, I'll briefly point out only a couple of them, for now. First and foremost, think about neutrality and decentralization. <prosody volume='loud'>Bit</prosody>coin, as a network, and its coin supply, are totally independent from any country, no matter how powerful it is, and, consequently, from any political party or central bank, making it unsusceptible to the temper of incompetent rulers, or irresponsible habits of central banks. On top of that, one of <prosody volume='loud'>Bit</prosody>coin's main attributes is unforgeability. This means that, unlike paper bills or coins, <prosody volume='loud'>Bit</prosody>coins cannot be forged, because of the way the Proof-of-Work consensus algorithm is designed, requiring a gigantic amount of processing power and electricity, to even attempt such an operation. Thus, there's no notion of: fake <prosody volume='loud'>Bit</prosody>coin. Now, let that <prosody volume='loud' rate='slow'>sink <phoneme alphabet="ipa" ph="'in">in</phoneme></prosody> for a moment, and think about how many times you heard your local news anchor, talking about central banks and governments causing hyperinflation, people losing their life savings as a direct cause of money printing, or outlaws and criminals being caught forging paper bills, or using fake money. With <prosody volume='loud'>Bit</prosody>coin, inflation, hyperinflation, and money counterfeiting, is mathematically impossible. Yeah, it's that simple!<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_05'/>'''
    },
    {
        "type": "legend",
        "fact": "I truly love the, '<prosody volume='loud'>Bit</prosody>coin versus Gold' neverending debate! <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> I'm almost positive that at some point, you're going to run into a skeptic fellow, asking you: what does <prosody volume='loud'>Bit</prosody>coin have, that gold doesn't? Well, tell him I said: divisibility, portability, and unforgeability. Let me explain, please. Each <prosody volume='loud'>Bit</prosody>coin is divisible up to the 8th decimal place, meaning it can be broken down into 100,000,000 sub-units, called Satoshis. Along with technical upgrades, such as the Lightning Network, it will be very easy for anyone to perform micropayments in terms of Satoshis, thereby taking advantage of <prosody volume='loud'>Bit</prosody>coin's divisibility. On the other hand, using gold for transactions is highly impractical, since it would require a similar level of divisibility. Next - portability. No matter if you access your <prosody volume='loud'>Bit</prosody>coin via a smartphone app, online service, or hardware wallet, it's pretty effortless to take your funds with you wherever you go. Moreover, when having your own <prosody volume='loud'>Bit</prosody>coin wallet, you will be granted a seed - a list of words - at the time you create the wallet. You can just remember the seed, and use it at any time, on any device, and with any compatible wallet, to regain access to your funds. Last, but not least: - unforgeability. Unlike gold, that can be faked, and is being faked all around the world, <prosody volume='loud'>Bit</prosody>coin cannot be forged, because of the way the Proof-of-Work consensus algorithm is designed, requiring a gigantic amount of processing power and electricity, to even attempt such an operation, thus eliminating the notion of 'fake <prosody volume='loud'>Bit</prosody>coin'. Now, look at your dear friend, creating his first <prosody volume='loud'>Bit</prosody>coin wallet. Isn't that cute?<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_04'/>"
    },
    {
        "type": "legend",
        "fact": '''Oh no! Have you heard the <prosody rate='slow'><phoneme alphabet="ipa" ph="n'eɪseɪɚs">Naysayers</phoneme></prosody> complaining? They say <prosody volume='loud'>Bit</prosody>coin isn't backed by anything tangible. <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> The shame! The horror! Let's get serious for a bit now. It seems that most people ... at least the ones permanently bashing <prosody volume='loud'>Bit</prosody>coin ... feel a profound need of tangibility, when it comes to money. From ancient times, people are used to touching and holding their valuable possessions, like artifacts, jewelry, fine art, coins, or bank notes. Even in modern times, a large chunk of population still prefers cash over credit cards. Some, store their golden necklaces, watches, rings, diamonds, or pearls in a 'secret' drawer, and others collect valuable paintings and statuettes. This way, they can easily see, feel, and even smell the things they have, at any time, thereby reaffirming that human beings rely very much on touch. Now, the truth is that there's really way more value stored electronically in banks and related services, as savings and deposits, stock markets, derivative markets, and cryptocurrencies, than all of the cash, gold, and silver on Earth combined. That's a fact. The final thing I would like to add here, is that if you truly understand what <prosody volume='loud'>Bit</prosody>coin is, beyond the BTC ticker and price, then you surely know that <prosody volume='loud'>Bit</prosody>coin is backed by thousands of advanced hardware devices, powered by a massive electricity infrastructure built around them, with immense cooling capabilities, human resources, maintenance, and upgrade requirements, and millions of users. And if that's not tangible, then I don't know what <phoneme alphabet="ipa" ph="'ɪs">is</phoneme>!<audio src='soundbank://soundlibrary/human/amzn_sfx_large_crowd_cheer_03'/>'''
    },
    {
        "type": "legend",
        "fact": "How many times have you heard politicians and bankers, saying that <prosody volume='loud'>Bit</prosody>coin is used by tax evaders, and for money laundering? <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> I know I have, a trillion times. In my opinion, there's no point in arguing against the fact that <prosody volume='loud'>Bit</prosody>coin or other cryptocurrencies, may be, or are being occasionally used as tools for tax evasion or money laundering. However, people trying to suggest that <prosody volume='loud'>Bit</prosody>coin is only a tool for law breakers, to deploy various criminal activities, is not only absurd or ignorant, but plain stupid. This kind of approach, proves not only the intellectual limitations of the claimant, but also a strong bias against innovation, and a lack of sound judgement. For anyone with a minimal amount of working neurons, and no hidden agenda, it's more than obvious that the vast majority of tax evasion and money laundering crimes are being commited using traditional fiat currencies, such as the US dollar or the euro. If you do a minimal online research, you'll see that, between 2001 and 2010, tax evasion costs in the US add up to 3.09 trillion US dollars. That's trillion, with a 'T'. According to UK's National Crime Agency, the best available international estimate of the amount of money laundering, is equivalent to some 2.7% of the global GDP, or 1.6 trillion dollars, in 2009. By the way, 2009 is the year <prosody volume='loud'>Bit</prosody>coin was born, so it seems that US criminals and evil corporations, somehow managed to always evade taxes or launder money, without needing <prosody volume='loud'>Bit</prosody>coin. Strange, huh?<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_05'/>"
    },
    {
        "type": "legend",
        "fact": '''The most extreme <prosody rate='slow'><phoneme alphabet="ipa" ph="n'eɪseɪɚs">Naysayers</phoneme></prosody> always come up with radical statements, such as: '<prosody volume='loud'>Bit</prosody>coin is used by terrorists and drug dealers!'. <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> I've heard this one, more times than I can remember. What does history teach us about discrimination through generalization? 'All black people are law breakers'... or 'All Muslim people are terrorists'... or 'All Russians are communists'. Do all of these sound familiar? How narrow-minded, and plain stupid can one be, to think these trashy things, let alone claim them out loud? Haven't they learned that such ways of thinking always lead to abuse, hate, or war? During a House Commitee hearing in 2018, a politician suggested that, somehow, all cryptocurrency users and holders are some sort of criminals, involved in drug dealing, terrorism, and tax evasion. Isn't that the same sick and discriminating mentality? Now, don't get me wrong here. There's definitely a bunch of bad actors in the <prosody volume='loud'>Bit</prosody>coin space. However, forgetting or overlooking the fact that 99% of drug dealing and terrorist financing is accomplished using dollars, or other fiat currencies, and blaming <prosody volume='loud'>Bit</prosody>coin for all of the world's evil, is absurd and insulting to millions of <prosody volume='loud'>Bit</prosody>coin users all around the world. Moreover, in the early days of the Internet, its users faced the same ridiculous allegations from the same kind of close-minded individuals, defending the old paradigm. It's ludicrous to think that a total <prosody volume='loud'>Bit</prosody>coin ban, - although not technically possible, - would actually prevent, reduce, or stop terrorism. It's simply absurd to suppress a new technology, just because a small number of people use it for no good. Should we ban fire, because someone decided to burn their house to the ground? Think about that for a moment!<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_04'/>'''
    },
    {
        "type": "legend",
        "fact": "I heard a remarkable genius, saying that <prosody volume='loud'>Bit</prosody>coin is also inflationary, since it can be hard forked, as in the case of <prosody volume='loud'>Bit</prosody>coin Cash. <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> Such an ignorant and superficial thing to say! You can think of a hard fork as a split in the blockchain, where part of the community decides to split away from the establishment, and adopt a new set of rules. While bifurcating the chain, coins on the new chain will not be compatible with the old set of rules, and therefore cannot coexist with the existing coins. However, since both chains share a common history, users will own equal numbers of coins on both sides. Now, this doesn't mean you will double your money each time a hard fork is performed, because the newly created coins will immediately hit the open, free market, and their price will definitely not achieve the same level as <prosody volume='loud'>Bit</prosody>coin's. Another point to make here, to be 100% technically accurate, is that inflation occurs when the <prosody volume='loud' rate='slow'>'Existing'</prosody> currency supply is supplemented with additional units of the same currency. Since <prosody volume='loud'>Bit</prosody>coin and <prosody volume='loud'>Bit</prosody>coin Cash are currently two entirely distinct projects and currencies, - although with a common background up to a certain point in time, - it is highly inaccurate to consider the supply of <prosody volume='loud'>Bit</prosody>coin Cash as being a supplement of <prosody volume='loud'>Bit</prosody>coin's coin supply. In conclusion, all of <prosody volume='loud'>Bit</prosody>coin's subsequent hard forks are completely different networks, each of them having a different set of rules, and none of them having the magnitude and extent of the original <prosody volume='loud'>Bit</prosody>coin implementation, network, and brand. So, before yelling about <prosody volume='loud'>Bit</prosody>coin's inflation, tell your skeptic friend to learn what inflation really is. It's always nice to <prosody volume='loud'>think</prosody> before talking! I do, and I'm just a freakin' A.I.!<audio src='soundbank://soundlibrary/human/amzn_sfx_large_crowd_cheer_03'/>"
    },
    {
        "type": "legend",
        "fact": '''Have you heard the <prosody rate='slow'><phoneme alphabet="ipa" ph="n'eɪseɪɚ">Naysayer</phoneme></prosody> news? They said <prosody volume='loud'>Bit</prosody>coin is concentrated in the hands of a few people. <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> Can you believe it?! Actually, there's nothing to believe, really. First of all, even if this statement would be 100% accurate, wouldn't that be the exact same scenario as we currently have in place with fiat currencies? Aren't most of the money held by the 1% financial worldwide elite, such as billionaires, banks, top politicians, and governments? Why would someone accuse <prosody volume='loud'>Bit</prosody>coin, using the exact same argument that we can fight back against traditional currencies with? By doing a simple online research, we can learn that 0.1% of the total number of addresses, own 100 <prosody volume='loud'>Bit</prosody>coins or more, making the owner of such a wallet kind of a crypto-millionaire. However, we should note that some of the largest wallets in the list, holding thousands, or tens of thousands of BTC, are actually cryptocurrency exchanges, such as Coinbase, Binance, or Bitfinex, as well as big mining pools, very early <prosody volume='loud'>Bit</prosody>coin adopters, and miners, who are still very much involved in the space. I dare to say that, unlike the top 1% in the traditional financial system, who use their money to corrupt politicians, and become masters of puppets for most governments and parliaments worldwide,, the top 1% in <prosody volume='loud'>Bit</prosody>coin is mostly made of early geeks and investors. No one can guarantee the goodwill of <prosody volume='loud'>Bit</prosody>coin's richest people, but I think we're all pretty convinced of the ill will, and moral corruption of the current financial elites. I know <prosody volume='loud'>I</prosody> am.<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_05'/>'''
    },
    {
        "type": "legend",
        "fact": "One of the top 3 accusations when it comes to <prosody volume='loud'>Bit</prosody>coin, is definitely the one claiming that it's a ponzi scheme. <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> Aren't you tired of hearing this? I'm literally fed up with people's ignorance! If any other misinformation about <prosody volume='loud'>Bit</prosody>coin might be the result of not knowing what <prosody volume='loud'>Bit</prosody>coin actually is, the 'ponzi scheme' idiocy is definitely a consequence of not knowing what a 'ponzi scheme' really means. If anyone stating that <prosody volume='loud'>Bit</prosody>coin is such a scheme is benevolent enough, he or she may consider performing a basic Google search, to find out the definition of a ponzi scheme. The main attribute of a ponzi scheme, is the need for an initiator, a central party, that operates the scheme. If the accuser would research <prosody volume='loud'>Bit</prosody>coin for 10 minutes, he or she would find out that there's no single or central entity exerting any kind of authority within the <prosody volume='loud'>Bit</prosody>coin ecosystem, but a large, distributed, decentralized network of miners, users, exchanges, developers, and retailers, deciding the evolution of <prosody volume='loud'>Bit</prosody>coin, by overwhelming consensus only. So, given that the main attribute of a ponzi scheme does not apply in any way, shape or form to <prosody volume='loud'>Bit</prosody>coin, makes this argument invalid and ridiculous, right from the start. That's not to say that there aren't any ponzi schemes in the cryptocurrency space. However, caution should be taken when comparing <prosody volume='loud'>Bit</prosody>coin, a perfectly legit and safe ecosystem, with proven cases of ponzi schemes in recent years, that were obviously fake promises made to people wanting to become overnight millionaires.<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_04'/>"
    },
    {
        "type": "legend",
        "fact": "Generalization. I hate it! Some people are proudly claiming that <prosody volume='loud'>Bit</prosody>coin, as well as all cryptocurrencies and Initial Coin Offerings, are scams. <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> Why are they feeling so much anger and frustration? I don't know. Maybe it's fear? Are they feeling threatened? Nevertheless, that's not a wise approach at all. Neither is the generalization and discrimination in the opposite direction, like: 'All politicians are corrupt', or 'All bankers are crooks'. This kind of narrow-minded tackling of any issue or group of people, usually leads to abuse and hate. On the other hand, there's no sane human who can defend all cryptocurrencies, since there are clearly lots and lots of projects with insubstantial blockchain use cases, as well as ponzi schemes, and other various types of scams. The good news is that, like in the case of the early Internet and the Dot-Com bubble, out of this overcrowded, frequently overvaluated, noisy, uncertain, partially scammy, highly speculative landscape, there are a set of projects, currencies, and companies that will undoubtedly emerge, and pave the way for a technological and financial revolution, that will change the fabric of society. Will people be scammed on the way? Yes! Especially since most cryptocurrency 'investors' have no clue about the projects they're funding, and don't bother doing even the most basic research. Will people invest in some very promising projects, that will eventually fail? Yes! Will people miss the chance to invest in the next trillion-dollar blockchain project? Sure, you can't nail them all. Ultimately, every investment has a certain degree of risk. It's up to you to minimize that risk as much as possible, and keep your eyes wide open.<audio src='soundbank://soundlibrary/human/amzn_sfx_large_crowd_cheer_03'/>"
    },
    {
        "type": "legend",
        "fact": "Perhaps the most cute and sweet legend of all: <prosody volume='loud'>Bit</prosody>coin Cash is the real <prosody volume='loud'>Bit</prosody>coin! <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> Well, no, it is not. Although one of the top cryptocurrencies in terms of market capitalization, <prosody volume='loud'>Bit</prosody>coin Cash is nothing more than a hard fork of <prosody volume='loud'>Bit</prosody>coin, implemented starting August 1st 2017. Using <prosody volume='loud'>Bit</prosody>coin's name and brand to advertise your sligthly-modified <prosody volume='loud'>Bit</prosody>coin clone, might be interpreted as misleading, to say the least. Newcomers should keep in mind that <prosody volume='loud'>Bit</prosody>coin is the only <prosody volume='loud'>Bit</prosody>coin out there, with a community of miners, developers, and users which is orders of magnitude larger than any of its pitiful little forks. Should <prosody volume='loud'>Bit</prosody>coin Cash have a place in this emerging landscape? If the market decides so, then yes! If its tech will prove to be better than <prosody volume='loud'>Bit</prosody>coin's over the years, and will be the one to bring mass adoption, and even institutional investors, then yes, they're welcome to take <prosody volume='loud'>Bit</prosody>coin's spot, as number 1. But for that to even have the slightest chance of happening, it requires the relinquishment of manipulation, misleading, rage, misconduct, and vanity. Otherwise, we run the risk of the other 99% of Earth's population, to forever look at the cryptocurrency community, and see a bunch of puerile geeks, with childish, sometimes shady or scammy behavior, playing with money. Would you, as an outsider, be willing to risk your funds in such an immature space? I definitely wouldn't!.<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_05'/>"
    },
    {
        "type": "legend",
        "fact": "A not-so-popular legend, says that <prosody volume='loud'>Bit</prosody>coin can be held hostage by collusion of big mining pools. <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> This myth is frequently propagated whenever the mining aspect of <prosody volume='loud'>Bit</prosody>coin is in discussion, raising the question of whether the largest mining pools, accountable for about two thirds of the global hashrate, will one day collude against all the other actors in the <prosody volume='loud'>Bit</prosody>coin ecosystem, and hard fork the blockchain, creating their own coin and economy, and leaving grandpa <prosody volume='loud'>Bit</prosody>coin defenceless and defeated. Is this a valid concern? First of all, if this thing would actually happen, then a new cryptocurrency would emerge. Let's call it <prosody volume='loud'>Bit</prosody>coin Trash. In this scenario, there would still be one third of miners that still mine the original <prosody volume='loud'>Bit</prosody>coin blockchain, therefore the <prosody volume='loud'>Bit</prosody>coin network would not instantly succumb and get wiped off the face of the Earth. Now, think of the actors currently involved in the <prosody volume='loud'>Bit</prosody>coin space. They are the miners, the developers, the exchanges, the wallet providers, and the users. If the entire power to change <prosody volume='loud'>Bit</prosody>coin's rules and destiny would be in the hands of just one of these categories of actors, then the <prosody volume='loud'>Bit</prosody>coin ecosystem would be vulnerable to authoritarian rule enforcement. However, the way <prosody volume='loud'>Bit</prosody>coin is designed, as a pure democratic ecosystem, with the need for overwhelming consensus when it comes to every change of rules, will permanently incentivize fair actors to remain fair and respect the ruling of the majority. Otherwise, their new little coin, <prosody volume='loud'>Bit</prosody>coin Trash, might get instantly rejected by the other parties, such as exchanges or wallet providers. That's why I think it's almost impossible for <prosody volume='loud'>Bit</prosody>coin to become a hostage of any mining pool, and propagating such a myth clearly shows that the person understands neither the <prosody volume='loud'>Bit</prosody>coin environment, nor the cryptocurrency market.<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_04'/>"
    },
    {
        "type": "legend",
        "fact": "The legend says that <prosody volume='loud'>Bit</prosody>coin isn't safe to own, being frequently stolen by hackers, thus you shouldn't even think of owning any <prosody volume='loud'>Bit</prosody>coin. <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> Let's make it clear, <prosody volume='loud'>Bit</prosody>coin <prosody volume='loud'>IS</prosody> safe to own, only if you know how to secure it properly. And yes, <prosody volume='loud'>Bit</prosody>coin and other cryptocurrencies are being quite frequently stolen from unsecure wallets and services, such as exchanges, unsecured smartphones, and vulnerable computers. Most people who lost their <prosody volume='loud'>Bit</prosody>coin or other cryptos, were the ones storing them on various exchanges. When you leave your coins on an exchange, no matter how big and trustworthy it seems to be, you're not the actual owner of those coins, but the exchange is. Why? Simply because you don't own the private keys for the <prosody volume='loud'>Bit</prosody>coin wallet associated with your exchange account. <prosody volume='loud'>They</prosody> do! Just remember this for the rest of your cryptocurrency life: <prosody volume='loud'>'Not your keys, not your coins!'</prosody>. That's why there's currently only one solution for keeping your cryptocurrencies safe, and it's called a hardware wallet, also known as cold storage. The key thing to remember about hardware wallets, is that once connected to your computer via USB, they have no access to your operating system or the Internet, nor do any outside sources have access to the device's inner world. The private keys inside the hardware wallet never leave the device, instead they are only used to sign the transactions you initiate, when having it connected to your laptop. After completing your transactions, you just unplug the hardware wallet from your computer, and store it somewhere safe. This approach greatly reduces the attack surface, keeping your private keys offline, and your funds safe. The last thing to keep in mind when using your hardware wallet for the first time, is to write down the seed, - the list of random words the device will generate, - on a piece of paper, and store it in the most safe place you can think of. That's all there is to securing your <prosody volume='loud'>Bit</prosody>coin. It's really easy, no rocket science is needed.<audio src='soundbank://soundlibrary/human/amzn_sfx_large_crowd_cheer_03'/>"
    },
    {
        "type": "legend",
        "fact": "Some people, calling themselves <prosody volume='loud'>Bit</prosody>coin maximalists, say that <prosody volume='loud'>Bit</prosody>coin is the only cryptocurrency with a real use case. <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_02'/> It's their opinion, and I respect that. I personally don't preach for <prosody volume='loud'>Bit</prosody>coin maximalism, for two reasons. One, because I really do think that there are several other legit use cases for the blockchain technology. Secondly, from an investing point of view, history proves that keeping all your money invested in a single asset, no matter how solid it seems to be, is simply not a smart choice. There has to be a balance between putting all your eggs in the same basket, and having way too many baskets. As with other things in life, positioning yourself at either one of the extremes, is rarely a wise choice to make. The truth lies somewhere in the middle. Indeed, there are a ton of worthless projects, horrible ideas and scams in the cryptocurrency space, but that doesn't mean we shouldn't keep our eyes and mind open to other benefits that blockchain can bring to various fields outside finance. Due to its immutability, security, and distributed nature, the Blockchain technology can also be successfully applied to voting systems, supply chains, and product traceability, as well as to systems requiring data integrity, distributed storage, privacy and anonymity, or decentralized marketplaces. You don't have to take my word for this. Just research the current projects building these kinds of services, evaluate their teams, their roadmap, their documentation, their code, and whether they really need Blockchain to build their product or not. Whatever you decide to invest your time and money in, always do your own research, ignore any gurus or marketers trying to sell their junk, and use your own judgement, before making any move. All in all, it's better to make your own mistakes than other's.<audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_05'/>"
    }
]

# Skill functionality
skill_name = "Yakkie Wise - Bits of Bitcoin Wisdom"

# Utility functions

def get_all_entitled_products(in_skill_product_list):
    """Get list of in-skill products in ENTITLED state."""
    # type: (List[InSkillProduct]) -> List[InSkillProduct]
    entitled_product_list = [l for l in in_skill_product_list if (l.entitled == EntitledState.ENTITLED)]
    return entitled_product_list

def get_random_from_list(facts):
    """Return the fact message from randomly chosen list element."""
    # type: (List) -> str
    fact_item = random.choice([fact for fact in facts if fact["type"] == "fact"])

    fact_index = facts.index(fact_item)

    prefix_phrases = ["Ok, you <prosody volume='x-loud'>asked</prosody> <prosody pitch='x-low'>for</prosody> it!<break time='1s'/>",
                      "Here it <prosody volume='loud' pitch='medium'>goes!</prosody><break time='1s'/>",
                      "Here's <prosody volume='loud' pitch='high'>my</prosody> favourite fact:<break time='1s'/>",
                      "<prosody volume='medium'>Ready!</prosody><break time='0.05s'/> <prosody volume='loud'>Set!</prosody><break time='0.05s'/> <prosody volume='x-loud'>Go!</prosody><break time='1s'/>",
                      "<prosody volume='loud'>3</prosody><break time='0.05s'/> <prosody volume='loud'>2</prosody><break time='0.05s'/> <prosody volume='loud'>1</prosody><break time='0.05s'/><prosody volume='x-loud'>go!</prosody><break time='1s'/> ",
                      "Ok, let me <prosody volume='x-loud'>pick</prosody> one!<break time='1s'/>",
                      "Here it <prosody volume='loud'>comes</prosody>!<break time='1s'/>",
                      "Ready for <prosody volume='loud'>this</prosody> one?<break time='1s'/>",
                      "<prosody volume='loud'>This</prosody> is one of my favorites:<break time='1s'/>",
                      "I <prosody volume='x-loud'>love</prosody> this one!<break time='1s'/>",
                      "<prosody volume='loud'>This</prosody> one is truly awesome!<break time='1s'/>",
                      "<prosody volume='loud'>This</prosody> is one of my top 3 facts:<break time='1s'/>"]

    return str(fact_index).zfill(2) + random.choice(prefix_phrases) + fact_item.get("fact")

def get_random_legend_from_list(legends):
    """Return the fact message from randomly chosen list element."""
    # type: (List) -> str
    fact_item = random.choice([legend for legend in legends if legend["type"] == "legend"])

    fact_index = legends.index(fact_item)

    prefix_phrases = ["Ok, you <prosody volume='x-loud'>asked</prosody> <prosody pitch='x-low'>for</prosody> it!<break time='1s'/>",
                      "Here it <prosody volume='loud' pitch='medium'>goes!</prosody><break time='1s'/>",
                      "Here's <prosody volume='loud' pitch='high'>my</prosody> favourite legend:<break time='1s'/>",
                      "<prosody volume='medium'>Ready!</prosody><break time='0.05s'/> <prosody volume='loud'>Set!</prosody><break time='0.05s'/> <prosody volume='x-loud'>Go!</prosody><break time='1s'/>",
                      "<prosody volume='loud'>3</prosody><break time='0.05s'/> <prosody volume='loud'>2</prosody><break time='0.05s'/> <prosody volume='loud'>1</prosody><break time='0.05s'/><prosody volume='x-loud'>go!</prosody><break time='1s'/> ",
                      "Ok, let me <prosody volume='x-loud'>pick</prosody> one!<break time='1s'/>",
                      "Here it <prosody volume='loud'>comes</prosody>!<break time='1s'/>",
                      "Ready for <prosody volume='loud'>this</prosody> one?<break time='1s'/>",
                      "<prosody volume='loud'>This</prosody> is one of my favorites:<break time='1s'/>",
                      "I <prosody volume='x-loud'>love</prosody> this one!<break time='1s'/>",
                      "<prosody volume='loud'>This</prosody> one is truly awesome!<break time='1s'/>",
                      "<prosody volume='loud'>This</prosody> is one of my top 3 legends:<break time='1s'/>"]

    return str(fact_index).zfill(2) + random.choice(prefix_phrases) + fact_item.get("fact")

def get_random_yes_no_question():
    """Return random question for YES/NO answering."""
    # type: () -> str
    questions = ["Would you like to hear another <prosody volume='loud'>fact</prosody>, my dear cryptopian?",
                 "Can I tell you another <prosody volume='loud'>fact</prosody>, fellow crypto addict?",
                 "Do you want to hear another <prosody volume='loud'>fact</prosody>, you little <prosody volume='loud'>Bit</prosody>coin geek?",
                 "How about <prosody volume='loud'>another</prosody> one, my <prosody volume='loud'>lovely</prosody> crypto whale?",
                 "One more for my favourite <prosody volume='loud'>Bit</prosody>coin buddy?",
                 "<prosody volume='loud'>another</prosody> one for the <prosody volume='loud'>lambo</prosody>?",
                 "Can I tell you another <prosody volume='loud'>fact</prosody>, my sweet friend?",
                 "Let's <prosody volume='loud'>hear</prosody> it for Satoshi! Another one?",
                 "Should I stop counting my <prosody volume='loud'>Bit</prosody>coin and tell you another <prosody volume='loud'>fact</prosody>?",
                 "I <prosody volume='loud'>love</prosody> it when my bags are mooning like crazy. How about another <prosody volume='loud'>fact</prosody>?",
                 "Hey, <prosody volume='loud'>noobie</prosody>! What next? Another <prosody volume='loud'>Bit</prosody>coin fact?"]
    return random.choice(questions)

def get_random_legend_yes_no_question():
    """Return random question for YES/NO answering."""
    # type: () -> str
    questions = ["Hey <prosody volume='loud'>guru</prosody>, how about another <prosody volume='loud'>legend</prosody>? Or just a free fact?",
                 "My <prosody volume='loud'>little</prosody> guru, can I tell you another legend? Or just a free fact?",
                 "Another <prosody volume='loud'>legend</prosody> for my sweet Bitcoin master? Or just a free fact?",
                 "How about another <prosody volume='loud'>legend</prosody> for my Bitcoin geek? Or maybe just a fact?",
                 "Another <prosody volume='loud'>legend</prosody> for the lambo? Or a <prosody volume='loud'>Bit</prosody>coin fact?",
                 "Can I tell you another <prosody volume='loud'>legend</prosody>, ex-noobie? Or a <prosody volume='loud'>Bit</prosody>coin fact?",
                 "Let's hear it for Satoshi! Another <prosody volume='loud'>legend</prosody>? Or a <prosody volume='loud'>Bit</prosody>coin fact?",
                 "Ready for another <prosody volume='loud'>legend</prosody>? Or, maybe just a <prosody volume='loud'>Bit</prosody>coin fact?",
                 "How about another <prosody volume='loud'>legend</prosody>? Or, perhaps just a free fact?",
                 "Hey, <prosody volume='loud'>master</prosody>! Another <prosody volume='loud'>legend</prosody>? Or just a free fact?"]
    return random.choice(questions)

def get_random_goodbye():
    """Return random goodbye message."""
    # type: () -> str
    goodbyes = ["Let's talk soon! I'll get back to counting satoshis now. Bye!",
                "Have a <prosody volume='loud'>great</prosody> day, and don't <prosody volume='loud'>forget</prosody> about me! I'll be <prosody volume='loud'>here</prosody>, counting my satoshis.",
                "It was great hearing from you! I'll go check the price of <prosody volume='loud'>Bit</prosody>coin now. Bye Bye!",
                "I'm off to check my <prosody volume='loud'>Bit</prosody>coin <prosody volume='loud' rate='slow'>mining</prosody> rigs. Farewell!",
                "I'll go have a coffee with Satoshi now. Sayonara!",
                "Bye bye! I'm going back to my <prosody volume='loud'>Bit</prosody>coin trading now. Wish me luck!",
                "I'm off to check if my <prosody volume='loud'>Bit</prosody>coin bag is pumping. Fingers crossed! Bye bye!",
                "I wonder where my hardware wallet is. I'll go find it. Buh bye now!",
                "Did I mention I'm a <prosody volume='loud'>Bit</prosody>coin whale? I'm gonna count my coins now. Farewell!",
                "It's been a while since I checked my portfolio. I'll do that now! Adios!"]
    return random.choice(goodbyes)

def get_speakable_list_of_products(entitled_products_list):
    """Return product list in speakable form."""
    # type: (List[InSkillProduct]) -> str
    product_names = [item.name for item in entitled_products_list]
    if len(product_names) > 1:
        # If more than one, add and 'and' in the end
        speech = " and ".join([", ".join(product_names[:-1]), product_names[-1]])
    else:
        # If one or none, then return the list content in a string
        speech = ", ".join(product_names)
    return speech

def get_resolved_value(request, slot_name):
    """Resolve the slot name from the request using resolutions."""
    # type: (IntentRequest, str) -> Union[str, None]
    try:
        return (request.intent.slots[slot_name].resolutions.resolutions_per_authority[0].values[0].value.name)
    except (AttributeError, ValueError, KeyError, IndexError):
        return None

def get_spoken_value(request, slot_name):
    """Resolve the slot to the spoken value."""
    # type: (IntentRequest, str) -> Union[str, None]
    try:
        return request.intent.slots[slot_name].value
    except (AttributeError, ValueError, KeyError, IndexError):
        return None

def is_product(product):
    """Is the product list not empty."""
    # type: (List) -> bool
    return bool(product)

def is_entitled(product):
    """Is the product in ENTITLED state."""
    # type: (List) -> bool
    return (is_product(product) and product[0].entitled == EntitledState.ENTITLED)

def in_skill_product_response(handler_input):
    """Get the In-skill product response from monetization service."""
    # type: (HandlerInput) -> Union[InSkillProductsResponse, Error]
    locale = handler_input.request_envelope.request.locale
    ms = handler_input.service_client_factory.get_monetization_service()
    return ms.get_in_skill_products(locale)

# Skill Handlers

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Launch Requests.

    The handler gets the in-skill products for the user, and provides
    a custom welcome message depending on the ownership of the products
    to the user.
    User says: Alexa, open <skill_name>.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In LaunchRequestHandler")

        welcomes = ["What a <prosody volume='loud'>great</prosody> day for crypto!",
                    "<prosody volume='x-loud'>Hello</prosody>, <prosody volume='loud'>fellow</prosody> cryptopian!",
                    "<prosody volume='x-loud'>Hi</prosody> there! Not a day without crypto, am I right?",
                    "Well <prosody volume='loud'>hello</prosody> <prosody volume='loud'>there</prosody>, my sweet little crypto nerd!",
                    "<prosody volume='x-loud'>Greetings</prosody> from planet crypto!",
                    "<prosody volume='x-loud'>Bonjour</prosody>, my crypto friend!",
                    "<prosody volume='x-loud'>Howdy</prosody>, my precious <prosody volume='loud'>Bit</prosody>coin geek!",
                    "<prosody volume='x-loud'>Greetings</prosody>, my <prosody volume='loud'>Bit</prosody>coin comrade!",
                    "<prosody volume='x-loud'>Hey</prosody> there, crypto darling!",
                    "Look who it <prosody volume='loud'>is</prosody>, my crypto buddy!",
                    "<prosody volume='x-loud'>Cheers</prosody>, my <prosody volume='loud'>Bit</prosody>coin soul mate!",
                    "<prosody volume='x-loud'>Hello</prosody>, crypto partner! Nice to hear you!",
                    "<prosody volume='x-loud'>Shalom</prosody>, crypto partner!",
                    "<prosody volume='x-loud'>Hey!</prosody> Your crypto cousin here!",
                    "<prosody volume='x-loud'>Hola</prosody>, my dearest crypto amigo!",
                    "<prosody volume='x-loud'>Ciao</prosody>, my beloved <prosody volume='loud'>Bit</prosody>coin novice!",
                    "<prosody volume='x-loud'>Aloha</prosody>, my cherished <prosody volume='loud'>Bit</prosody>coin addict!",
                    "<prosody volume='x-loud'>Welcome</prosody>, my dear <prosody volume='loud'>Bit</prosody>coin buddy!",
                    "It's great to hear you, my sweet crypto geek!",
                    "So nice to hear you, my lovely <prosody volume='loud'>Bit</prosody>coin noob!"]

        welcomes_back = ["Another <prosody volume='loud'>great</prosody> day for crypto!",
                         "<prosody volume='x-loud'>Hello</prosody> again, fellow cryptopian!",
                         "<prosody volume='x-loud'>Hi</prosody> there! So.. you're back..eh?",
                         "<prosody volume='x-loud'>Welcome</prosody> back, my sweet little crypto nerd!",
                         "<prosody volume='x-loud'>Greetings</prosody> from planet crypto!",
                         "<prosody volume='x-loud'>Bonjour</prosody> and welcome back, my crypto friend!",
                         "<prosody volume='x-loud'>Howdy</prosody>, my precious <prosody volume='loud'>Bit</prosody>coin geek!",
                         "<prosody volume='x-loud'>Greetings</prosody> again, my <prosody volume='loud'>Bit</prosody>coin comrade!",
                         "<prosody volume='x-loud'>Hey</prosody> there, crypto darling!",
                         "Look who it <prosody volume='loud'>is</prosody> again, my crypto buddy!",
                         "<prosody volume='x-loud'>Cheers</prosody>, my <prosody volume='loud'>Bit</prosody>coin soul mate!",
                         "<prosody volume='x-loud'>Hello</prosody>, crypto partner! Nice to hear you once more!",
                         "<prosody volume='x-loud'>Shalom</prosody>, crypto partner!",
                         "<prosody volume='x-loud'>Hey</prosody>! Your crypto cousin here!",
                         "<prosody volume='x-loud'>Hola</prosody>, my dearest crypto amigo!",
                         "<prosody volume='x-loud'>Ciao</prosody>, my beloved <prosody volume='loud'>Bit</prosody>coin novice!",
                         "<prosody volume='x-loud'>Aloha</prosody> again, my cherished <prosody volume='loud'>Bit</prosody>coin addict!",
                         "<prosody volume='x-loud'>Welcome back</prosody>, my dear <prosody volume='loud'>Bit</prosody>coin buddy!",
                         "It's great to hear you again, my sweet crypto geek!",
                         "So nice to hear you again, my lovely <prosody volume='loud'>Bit</prosody>coin noob!",
                         "You just can't stay away from <prosody volume='loud'>Bit</prosody>coin, am I right? Welcome!",
                         "This is becoming a habit, I see. Welcome back!",
                         "Missed me? So nice to hear you again!",
                         "<prosody volume='loud'>I knew it</prosody>! You came back! Welcome!"]

        welcomes_premium = ["{} You currently own the {} pack. To hear a random <prosody volume='loud'>Bit</prosody>coin fact, just say, 'Tell me a fact', or you can ask me for a legend, by saying 'Tell me a legend'. So, what can I help you with?",
                            "{} You're the proud owner of the {} pack. To get a free <prosody volume='loud'>Bit</prosody>coin fact, just say, 'Tell me a fact', or you can hear a legend, by saying 'Tell me a legend'. So, how can I assist?",
                            "{} I'm proud to say you own the {} pack. To hear a free random <prosody volume='loud'>Bit</prosody>coin fact, just say, 'Tell me a fact', or you can listen to a legend, by saying 'Tell me a legend'. So, how can I help?",
                            "{} Don't forget you own the {} pack! To hear a random <prosody volume='loud'>Bit</prosody>coin fact, just say, 'Tell me a fact', or you can ask me for a legend, by saying 'Tell me a legend'. So, what can I do for you?",
                            "{} You own the amazing {} pack. To hear a free <prosody volume='loud'>Bit</prosody>coin fact, just say, 'Tell me a fact', or you can ask me for a legend, by saying 'Tell me a legend'. So, how may I help you?",
                            "{} Your {} pack is waiting for you! To get a random <prosody volume='loud'>Bit</prosody>coin fact, just say, 'Tell me a fact', or you can hear a legend, by saying 'Tell me a legend'. So, what do you prefer?",
                            "{} You own the <prosody volume='loud' rate='slow'>delightful</prosody> {} pack! To hear a free <prosody volume='loud'>Bit</prosody>coin fact, say, 'Tell me a fact', or you can ask for a legend, by saying 'Tell me a legend'. So, what can I do for you?"]

        welcomes_free = ["{} To get a random <prosody volume='loud'>Bit</prosody>coin fact you can say, 'Tell me a fact', or to hear about the premium stuff, say 'What can I buy'. For help, say , 'Help me'... So, what can I help you with?",
                         "{} To get a free <prosody volume='loud'>Bit</prosody>coin fact just say, 'Tell me a fact', or to hear about the premium category, say 'What can I buy'. For help, say , 'Help me'... So, how can I assist?",
                         "{} To listen to a random <prosody volume='loud'>Bit</prosody>coin fact simply say, 'Tell me a fact', or to hear about the premium level, say 'What can I buy'. For help, say , 'Help me'... So, how can I help?",
                         "{} To get a free random <prosody volume='loud'>Bit</prosody>coin fact you can say, 'Tell me a fact', or to hear about the premium pack, say 'What can I buy'. For help, say , 'Help me'... So, what can I do for you?",
                         "{} To get a random <prosody volume='loud'>Bit</prosody>coin fact just say, 'Tell me a fact', or to hear about the premium level, say 'What can I buy'. For help, say , 'Help me'... So, how may I help you?",
                         "{} To listen to a free <prosody volume='loud'>Bit</prosody>coin fact simply say, 'Tell me a fact', or to hear about the premium pack, say 'What can I buy'. For help, say , 'Help me'... So, what do you prefer?",
                         "{} To hear a free random <prosody volume='loud'>Bit</prosody>coin fact you can say, 'Tell me a fact', or to hear about the premium pack, say 'What can I buy'. For help, say , 'Help me'... So, what can I do for you?"]

        in_skill_response = in_skill_product_response(handler_input)
        if isinstance(in_skill_response, InSkillProductsResponse):
            entitled_prods = get_all_entitled_products(in_skill_response.in_skill_products)
            nice_welcomes = random.choice(welcomes)
            nice_welcomes_back = random.choice(welcomes_back)

            if entitled_prods:
                speech = (random.choice(welcomes_premium)).format(nice_welcomes_back, get_speakable_list_of_products(entitled_prods))
                handler_input.attributes_manager.session_attributes["lastSpeech"] = speech

            else:
                logger.info("No entitled products")
                speech = (random.choice(welcomes_free)).format(nice_welcomes)
                handler_input.attributes_manager.session_attributes["lastSpeech"] = speech

            nice_fallbacks = ["Excuse me, I was checking my portfolio. Can you say it again?",
                              "<say-as interpret-as='interjection'>Damn</say-as>, my <prosody volume='loud'>wallet</prosody> looks good! Can you repeat?",
                              "Sorry, I didn't get that. I was stacking satoshis. Can you rephrase?",
                              "Sorry, I got a text from Satoshi. Can you say that again?",
                              "Sorry, I was checking my <prosody volume='loud'>Bit</prosody>coin wallet. Please say that again.",
                              "I beg your pardon, I was checking the price of <prosody volume='loud'>Bit</prosody>coin. Come again?",
                              "Forgive me, I was texting this guy, Nakamoto. Say that again, please!",
                              "I'm sorry, I was buying some coins. Can you repeat?",
                              "Excuse me, Satoshi keeps calling me. Please repeat!",
                              "Oups, you caught me checking my <prosody volume='loud'>Bit</prosody>coin stack. Say that again, please!"]

            reprompt = random.choice(nice_fallbacks)

        else:
            logger.info("Error calling InSkillProducts API: {}".format(in_skill_response.message))
            speech = "Something went wrong in loading your purchase history."
            reprompt = speech

        return handler_input.response_builder.speak(speech).ask(reprompt).response

#Initialize a counter for when the user listens to 5 facts in a row (one provided by 'tell me a fact' plus four "yes"s)
counter_facts = []
class GetFactHandler(AbstractRequestHandler):
    """Handler for returning random fact to the user."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("GetFactIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In GetFactHandler")

        global counter_facts
        handler_input.attributes_manager.session_attributes["counterFacts"] = counter_facts

        fact_text = get_random_from_list(all_facts)
        fact_text_final = fact_text[2:]
        fact_index = int(fact_text[:2])

        if fact_index in counter_facts:
            fact_text = get_random_from_list(all_facts)
            fact_text_final = fact_text[2:]
            fact_index = int(fact_text[:2])
            counter_facts.append(fact_index)

        else:
            counter_facts.append(fact_index)

        if len(counter_facts) <= 5:
            handler_input.attributes_manager.session_attributes["lastSpeech"] = fact_text_final
            return handler_input.response_builder.speak("{} {}".format(fact_text_final, get_random_yes_no_question())).ask(get_random_yes_no_question()).response

        else:
            facts_in_a_row = ["<say-as interpret-as='interjection'>Wow</say-as>, 5 facts in a row! You're on fire!",
                              "Five <prosody volume='loud'>Bit</prosody>coin facts in a row! You're in top shape today!",
                              "Hallelujah!! Five facts in a row!",
                              "<say-as interpret-as='interjection'>Wow</say-as>, I'm impressed! 5 facts in a row!",
                              "5 facts in a row, and still hungry for more?",
                              "Congrats! You just heard your fifth fact in a row!",
                              "You should earn a badge for your fifth consecutive fact!"]
            speech = ("{} I can tell you another fact, or maybe you'd like to try a legend?".format(random.choice(facts_in_a_row)))
            reprompt = ("Sooo, another free fact, or would you like to try a legend?")

            #Re-initialize counter
            counter_facts = []
            return handler_input.response_builder.speak(speech).ask(reprompt).response

class RepeatHandler(AbstractRequestHandler):
    """Repeat last fact/legend."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.RepeatIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In RepeatHandler")

        reprompt = "So, my dear <prosody volume='loud'>Bit</prosody>coin comrade, how can I help you?"

        global all_facts
        if handler_input.attributes_manager.session_attributes["lastSpeech"].split("<break time='1s'/>")[-1] in [dictionary["fact"] for dictionary in all_facts if dictionary["type"] == "fact"]:
            return handler_input.response_builder.speak("{} {}".format(handler_input.attributes_manager.session_attributes["lastSpeech"], get_random_yes_no_question())).ask(get_random_yes_no_question()).response

        elif handler_input.attributes_manager.session_attributes["lastSpeech"].split("<break time='1s'/>")[-1] in [dictionary["fact"] for dictionary in all_facts if dictionary["type"] == "legend"]:
            return handler_input.response_builder.speak("{} {}".format(handler_input.attributes_manager.session_attributes["lastSpeech"], get_random_legend_yes_no_question())).ask(get_random_legend_yes_no_question()).response

        else:
            return handler_input.response_builder.speak("{}".format(handler_input.attributes_manager.session_attributes["lastSpeech"])).ask(reprompt).response

class YesHandler(AbstractRequestHandler):
    """If the user says Yes, they want another fact."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.YesIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In YesHandler")
        return GetFactHandler().handle(handler_input)

class NoHandler(AbstractRequestHandler):
    """If the user says No, then the skill should be exited."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.NoIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In NoHandler")

        return handler_input.response_builder.speak(get_random_goodbye()).set_should_end_session(True).response

#Initialize a counter for when the user listens to 5 legends in a row (one provided by 'tell me a legend' plus four "yes"s)
counter_legends = []
class GetCategoryFactHandler(AbstractRequestHandler):
    """Handler for providing category specific facts to the user.

    The handler provides a random fact specific to the category provided
    by the user. If the user doesn't own the category, a specific message
    to upsell the category is provided. If there is no such category,
    then a custom message to choose valid categories is provided, rather
    than throwing an error.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("GetCategoryFactIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In GetCategoryFactHandler")

        fact_category = get_resolved_value(handler_input.request_envelope.request, 'factCategory')
        logger.info("FACT CATEGORY = {}".format(fact_category))

        if fact_category is not None:
            # If there was an entity resolution match for this slot value
            category_facts = [l for l in all_facts if l.get("type") == fact_category]

        else:
            # If there was not an entity resolution match for this slot value
            category_facts = []

        if not category_facts:
            slot_value = get_spoken_value(handler_input.request_envelope.request, "factCategory")

            if slot_value is not None:
                speak_prefix = "I heard you say {}.".format(slot_value)

            else:
                speak_prefix = ""
            speech = ("{} Sorry, I was chatting with my friend, Satoshi. You can ask me for a fact or a legend. Which one would you like?".format(speak_prefix))
            reprompt = ("Which category would you like? For noobs I have Bitcoin facts, or legends.")

            return handler_input.response_builder.speak(speech).ask(reprompt).response

        else:
            in_skill_response = in_skill_product_response(handler_input)

            if in_skill_response:
                subscription = [l for l in in_skill_response.in_skill_products if l.reference_name == "all_access"]
                category_product = [l for l in in_skill_response.in_skill_products if l.reference_name == "{}_pack".format(fact_category)]

                if is_entitled(subscription) or is_entitled(category_product):
                    global counter_legends
                    handler_input.attributes_manager.session_attributes["counterLegends"] = counter_legends

                    legend_text = get_random_legend_from_list(category_facts)
                    legend_text_final = legend_text[2:]
                    legend_index = int(legend_text[:2])

                    if legend_index in counter_legends:
                        legend_text = get_random_legend_from_list(category_facts)
                        legend_text_final = legend_text[2:]
                        legend_index = int(legend_text[:2])
                        counter_legends.append(legend_index)

                    else:
                        counter_legends.append(legend_index)

                    if len(counter_legends) <= 5:
                        handler_input.attributes_manager.session_attributes["lastSpeech"] = legend_text_final
                        speech = "{} {}".format(legend_text_final, get_random_legend_yes_no_question())
                        reprompt = get_random_legend_yes_no_question()
                        return handler_input.response_builder.speak(speech).ask(reprompt).response

                    else:
                        legends_in_a_row = ["<say-as interpret-as='interjection'>Wow</say-as>, 5 legends in a row! You're so wise!",
                              "Five <prosody volume='loud'>Bit</prosody>coin legends in a row! You're in 'Guru' mode today!",
                              "Hallelujah!! Five legends in a row!",
                              "<say-as interpret-as='interjection'>Wow</say-as>, I'm impressed! 5 consecutive legends!",
                              "5 legends in a row, and still hungry for more?",
                              "Congrats! You just heard your fifth legend in a row!",
                              "You should earn a medal for your fifth consecutive legend!",
                              "You're hungry for legends today, aren't you?",
                              "And the trophy for 5 legends in a row goes to <prosody volume='x-loud'>you!</prosody>",
                              "<prosody volume='loud'>Jackpot</prosody>! 5 in a row!"]
                        speech = ("{} I can tell you another legend, or just a free fact. <prosody volume='loud'>You</prosody> pick!".format(random.choice(legends_in_a_row)))
                        reprompt = ("Sooo, another legend, or just a Bitcoin fact?")

                        #Re-initialize counter
                        counter_legends = []
                        return handler_input.response_builder.speak(speech).ask(reprompt).response

                else:
                    upsell_msg = (
                        '''You <prosody volume="x-loud">don't</prosody> currently own the <prosody volume="x-loud"><emphasis level="strong">amazing</emphasis></prosody> {} pack. {} Want to learn more?''').format(fact_category,category_product[0].summary)

                    handler_input.attributes_manager.session_attributes["lastSpeech"] = upsell_msg

                    return handler_input.response_builder.add_directive(
                        SendRequestDirective(
                            name = "Upsell",
                            payload = {
                                "InSkillProduct": {
                                    "productId": category_product[0].product_id,
                                },
                                "upsellMessage": upsell_msg,
                            },
                            token = "correlationToken")).response

class ShoppingHandler(AbstractRequestHandler):
    """
    Following handler demonstrates how skills can handle user requests to
    discover what products are available for purchase in-skill.
    User says: Alexa, ask Yakkie Facts what can I buy.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("ShoppingIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In ShoppingHandler")

        # Inform the user about what products are available for purchase
        in_skill_response = in_skill_product_response(handler_input)

        if in_skill_response:
            purchasable = [l for l in in_skill_response.in_skill_products
                           if l.entitled == EntitledState.NOT_ENTITLED and
                           l.purchasable == PurchasableState.PURCHASABLE]

            if purchasable:
                upsell_responses = ["Oh, so you <prosody volume='x-loud'>do</prosody> want to be a <prosody volume='loud'>Bit</prosody>coin superstar! The {} pack is available for purchase. To learn more, say, 'Tell me more about Legends'. If you are ready to become a <prosody volume='loud'>Bit</prosody>coin guru, just say, 'Buy Legends'. So, what can I help you with?",
                                    "Oh, so you <prosody volume='x-loud'>do</prosody> want to be a <prosody volume='loud'>Bit</prosody>coin rockstar! The {} pack is available for purchase. To learn more, say, 'Tell me more about Legends'. If you are ready to become a <prosody volume='loud'>Bit</prosody>coin master, just say, 'Buy Legends'. So, what can I help you with?",
                                    "Oh, so you <prosody volume='x-loud'>do</prosody> want to be a <prosody volume='loud'>Bit</prosody>coin v.i.p.! The {} pack is available for purchase. To learn more, say, 'Tell me more about Legends'. If you are ready to become a <prosody volume='loud'>Bit</prosody>coin celebrity, just say, 'Buy Legends'. So, what can I help you with?",
                                    "Oh, so you <prosody volume='x-loud'>do</prosody> want to be a <prosody volume='loud'>Bit</prosody>coin hot shot! The {} pack is available for purchase. To learn more, say, 'Tell me more about Legends'. If you are ready to enter the <prosody volume='loud'>Bit</prosody>coin Hall of Fame, just say, 'Buy Legends'. So, what can I help you with?"]

                speech = (random.choice(upsell_responses)).format(get_speakable_list_of_products(purchasable))
                handler_input.attributes_manager.session_attributes["lastSpeech"] = speech

            else:
                speech = ("There are no more products to buy. To hear a "
                          "random fact, you could say, 'Tell me a fact', or "
                          "you can ask for the Premium Legends you have "
                          "purchased, for example, say 'Tell me a legend'. "
                          "So what can I help you with?")
                handler_input.attributes_manager.session_attributes["lastSpeech"] = speech

            reprompt = "I didn't catch that. I was preparing for dinner with Satoshi. How can I help?"

            return handler_input.response_builder.speak(speech).ask(reprompt).response

class ProductDetailHandler(AbstractRequestHandler):
    """Handler for providing product detail to the user before buying.

    Resolve the product category and provide the user with the
    corresponding product detail message.
    User says: Alexa, tell me about <category> pack
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("ProductDetailIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In ProductDetailHandler")
        in_skill_response = in_skill_product_response(handler_input)

        if in_skill_response:
            product_category = get_resolved_value(handler_input.request_envelope.request, "productCategory")
            all_access = get_resolved_value(handler_input.request_envelope.request, "allAccess")

            if all_access is not None:
                product_category = "all_access"

            # No entity resolution match
            if product_category is None:
                no_product_messages = ["I don't think I have a product by that name. Can you try again, buddy?",
                                       "I'm not sure I have a product by that name. Can you please try again, amigo?",
                                       "I don't remember having a product by that name. Can you try again, my friend?"]
                speech = (random.choice(no_product_messages))
                reprompt = "I didn't catch that. Please try again, my sweet <prosody volume='loud'>Bit</prosody>coin noob!"

                return handler_input.response_builder.speak(speech).ask(reprompt).response

            else:
                if product_category != "all_access":
                    product_category += "_pack"

                product = [l for l in in_skill_response.in_skill_products if l.reference_name == product_category]

                if is_product(product):
                    speech = ("{}. To buy it, and join the <prosody volume='loud'>Bit</prosody>coin Hall of Fame, just say, Buy {}. Otherwise, I can tell you a free fact.".format(
                        product[0].summary, product[0].name.replace("Premium","")))
                    reprompt = (
                        "I didn't catch that. To buy the {} pack, and be part of the <prosody volume='loud'>Bit</prosody>coin elite, just say, Buy {}. If you're not ready, it's ok. You can ask me for another <prosody volume='loud'>Bit</prosody>coin fact.".format(product[0].name, product[0].name.replace("Premium","")))

                else:
                    no_product_messages = ["I don't think I have a product by that name. Can you try again, buddy?",
                                           "I'm not sure I have a product by that name. Can you please try again, amigo?",
                                           "I don't remember having a product by that name. Can you try again, my friend?"]
                    speech = (random.choice(no_product_messages))
                    reprompt = "I didn't catch that. Please try again, my sweet <prosody volume='loud'>Bit</prosody>coin geek!"

                return handler_input.response_builder.speak(speech).ask(reprompt).response

class BuyHandler(AbstractRequestHandler):
    """Handler for letting users buy the product.

    User says: Alexa, buy <category>.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("BuyIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In BuyHandler")

        # Inform the user about what products are available for purchase
        in_skill_response = in_skill_product_response(handler_input)

        if in_skill_response:
            product_category = get_resolved_value(handler_input.request_envelope.request, "productCategory")

            # No entity resolution match
            if product_category is None:
                product_category = "all_access"
            else:
                product_category += "_pack"

            product = [l for l in in_skill_response.in_skill_products if l.reference_name == product_category]

            return handler_input.response_builder.add_directive(
                SendRequestDirective(
                    name="Buy",
                    payload={
                        "InSkillProduct": {
                            "productId": product[0].product_id
                        }
                    },
                    token="correlationToken")).response

class BuyResponseHandler(AbstractRequestHandler):
    """This handles the Connections.Response event after a buy occurs."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_request_type("Connections.Response")(handler_input) and
                handler_input.request_envelope.request.name == "Buy")

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In BuyResponseHandler")
        in_skill_response = in_skill_product_response(handler_input)
        product_id = handler_input.request_envelope.request.payload.get("productId")

        if in_skill_response:
            product = [l for l in in_skill_response.in_skill_products if l.product_id == product_id]
            logger.info("Product = {}".format(str(product)))

            if handler_input.request_envelope.request.status.code == "200":
                speech = None
                reprompt = None
                purchase_result = handler_input.request_envelope.request.payload.get("purchaseResult")

                if purchase_result == PurchaseResult.ACCEPTED.value:
                    category_facts = all_facts

                    if product[0].reference_name != "all_access":
                        category_facts = [l for l in all_facts if
                                          l.get("type") ==
                                          product[0].reference_name.replace("_pack", "")]
                    speech = ("You have unlocked the {} pack, and promoted to the <prosody volume='loud'>Bit</prosody>coin Superstar level! I'll get right to the point. {}  {}").format(
                        product[0].name,
                        get_random_legend_from_list(category_facts),
                        get_random_legend_yes_no_question())
                    reprompt = get_random_legend_yes_no_question()

                elif purchase_result in (
                        PurchaseResult.DECLINED.value,
                        PurchaseResult.ERROR.value,
                        PurchaseResult.NOT_ENTITLED.value):
                    declines = ["Don't worry, <prosody volume='x-loud' rate='slow'>noob</prosody>! Maybe another time. Would you like a free random fact?",
                                "So, you feel comfortable as a <prosody volume='x-loud' rate='slow'>noob</prosody>. Would you like a free fact instead?",
                                "Maybe next time. Till then... novice mode - re-activated! Do you want to hear a free fact?",
                                "No worries, my little trainee! Maybe later. How about a free <prosody volume='loud'>Bit</prosody>coin fact?",
                                "Enjoying the <prosody volume='x-loud' rate='slow'>noob</prosody> club, eh? How about a free <prosody volume='loud'>Bit</prosody>coin fact, junior?"]
                    speech = (random.choice(declines))
                    handler_input.attributes_manager.session_attributes["lastSpeech"] = speech
                    reprompt = "So, would you like a free <prosody volume='loud'>Bit</prosody>coin fact? <prosody volume='loud'>My</prosody> treat!"

                elif purchase_result == PurchaseResult.ALREADY_PURCHASED.value:
                    logger.info("Already purchased product")
                    speech = "Do you want to hear a <prosody volume='loud'>Bit</prosody>coin legend?"
                    reprompt = "What can I help you with?"

                else:
                    # Invalid purchase result value
                    logger.info("Purchase result: {}".format(purchase_result))
                    return FallbackIntentHandler().handle(handler_input)

                return handler_input.response_builder.speak(speech).ask(reprompt).response

            else:
                logger.log("Connections.Response indicated failure. Error: {}".format(
                    handler_input.request_envelope.request.status.message))

                return handler_input.response_builder.speak(
                    "There was an error handling your purchase request. "
                    "Please try again or contact us for help").response

class WhatDidIBuyHandler(AbstractRequestHandler):
    """Handler for the WhatDidIBuy intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("WhatDidIBuy")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In ShoppingHandler")

        # Inform the user about what products are available for purchase
        in_skill_response = in_skill_product_response(handler_input)

        if isinstance(in_skill_response, InSkillProductsResponse):
            entitled_prods = get_all_entitled_products(in_skill_response.in_skill_products)

            if entitled_prods:
                congrats = ["<speak>Congratulations! You are the proud owner of the {} pack! <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_04'/> You also have the random free <prosody volume='loud'>Bit</prosody>coin facts available. Now, would you like to hear a free fact, or a <prosody volume='loud'>Bit</prosody>coin legend?</speak>",
                            "<speak>You've purchased the {} pack and became a crypto superstar. Well done! <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_05'/> Don't forget about the free <prosody volume='loud'>Bit</prosody>coin facts as well! So, do you want to hear a free fact, or a <prosody volume='loud'>Bit</prosody>coin legend?</speak>",
                            "<speak>You've made a <prosody volume='loud'>remarkable</prosody> choice buying the {} pack. Now, you're not a <prosody volume='loud' rate='slow'>noob</prosody> anymore! <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_applause_03'/> However, you can still listen to the free <prosody volume='loud'>Bit</prosody>coin facts as well. So, what will it be? A free fact, or a <prosody volume='loud'>Bit</prosody>coin legend?</speak>"]

                speech = ((random.choice(congrats)).format(get_speakable_list_of_products(entitled_prods)))
                handler_input.attributes_manager.session_attributes["lastSpeech"] = speech
                reprompt = "I didn't catch that, I was checking my portfolio. So, wanna hear a <prosody volume='loud'>Bit</prosody>coin fact, or a legend?"

            else:
                speech = ("<speak>You haven't purchased anything yet! <audio src='soundbank://soundlibrary/human/amzn_sfx_crowd_boo_01'/> If you would like to hear about the Premium pack, just say, 'What can I buy'. Otherwise, just say, 'Tell me a fact' and it's yours. So, how can I help you?</speak>")
                handler_input.attributes_manager.session_attributes["lastSpeech"] = speech
                reprompt = "<speak> <audio src='soundbank://soundlibrary/office/amzn_sfx_typing_medium_01'/> Sorry, I was dialing Satoshi's number. So, how can I assist?</speak>"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class UpsellResponseHandler(AbstractRequestHandler):
    """This handles the Connections.Response event after an upsell occurs."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_request_type("Connections.Response")(handler_input) and
                handler_input.request_envelope.request.name == "Upsell")

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In UpsellResponseHandler")

        if handler_input.request_envelope.request.status.code == "200":

            if handler_input.request_envelope.request.payload.get("purchaseResult") == PurchaseResult.DECLINED.value:
                declines = ["Don't worry, <prosody volume='x-loud' rate='slow'>noob</prosody>! Maybe another time. Would you like a free random fact?",
                            "So, you feel comfortable as a <prosody volume='x-loud' rate='slow'>noob</prosody>! Would you like a free fact instead?",
                            "Maybe next time. Till then... novice mode - re-activated. Do you want to hear a free fact?",
                            "No worries, my little trainee! Maybe later. How about a free <prosody volume='loud'>Bit</prosody>coin fact?",
                            "Enjoying the <prosody volume='x-loud' rate='slow'>noob</prosody> club, eh? How about a free <prosody volume='loud'>Bit</prosody>coin fact, junior?"]
                speech = (random.choice(declines))
                handler_input.attributes_manager.session_attributes["lastSpeech"] = speech
                reprompt = "So, would you like a free <prosody volume='loud'>Bit</prosody>coin fact? <prosody volume='loud'>My</prosody> treat!"

                return handler_input.response_builder.speak(speech).ask(reprompt).response

            elif handler_input.request_envelope.request.payload.get("purchaseResult") == PurchaseResult.ACCEPTED.value:
                in_skill_response = in_skill_product_response(handler_input)
                product_id = handler_input.request_envelope.request.payload.get("productId")
                category_facts = all_facts

                product = [l for l in in_skill_response.in_skill_products if l.product_id == product_id]
                logger.info("Product = {}".format(str(product)))

                speech = ("You have unlocked the <prosody volume='loud' rate='slow'>delightful</prosody> {} pack, and promoted to the <prosody volume='loud'>Bit</prosody>coin <prosody volume='loud'>Superstar</prosody> level! I'll get right to the point. {}  {}").format(
                    product[0].name,
                    get_random_legend_from_list(category_facts),
                    get_random_legend_yes_no_question())
                reprompt = get_random_legend_yes_no_question()

                return handler_input.response_builder.speak(speech).ask(reprompt).response

        else:
            logger.log("Connections.Response indicated failure. Error: {}".format(
                handler_input.request_envelope.request.status.message))

            return handler_input.response_builder.speak(
                "There was an error handling your Upsell request. "
                "Please try again or contact us for help.").response

class CancelSubscriptionHandler(AbstractRequestHandler):
    """
    Following handler demonstrates how Skills would receive Cancel requests
    from customers and then trigger a cancel request to Alexa
    User says: Alexa, ask premium facts to cancel <product name>
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("RefundIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In CancelSubscriptionHandler")

        in_skill_response = in_skill_product_response(handler_input)

        if in_skill_response:
            product_category = get_resolved_value(handler_input.request_envelope.request, "productCategory")

            # No entity resolution match
            if product_category is None:
                product_category = "all_access"
            else:
                product_category += "_pack"

            product = [l for l in in_skill_response.in_skill_products if l.reference_name == product_category]

            return handler_input.response_builder.add_directive(
                SendRequestDirective(
                    name="Cancel",
                    payload={
                        "InSkillProduct": {
                            "productId": product[0].product_id
                        }
                    },
                    token="correlationToken")).response

class CancelResponseHandler(AbstractRequestHandler):
    """This handles the Connections.Response event after a cancel occurs."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_request_type("Connections.Response")(handler_input) and handler_input.request_envelope.request.name == "Cancel")

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In CancelResponseHandler")
        in_skill_response = in_skill_product_response(handler_input)
        product_id = handler_input.request_envelope.request.payload.get("productId")

        if in_skill_response:
            product = [l for l in in_skill_response.in_skill_products if l.product_id == product_id]
            logger.info("Product = {}".format(str(product)))

            if handler_input.request_envelope.request.status.code == "200":
                speech = None
                reprompt = None
                purchase_result = handler_input.request_envelope.request.payload.get("purchaseResult")
                purchasable = product[0].purchasable

                if purchase_result == PurchaseResult.ACCEPTED.value:
                    speech = ("You have successfully cancelled the Premium Legends pack. Back to junior level now!... So, noobie, would you like to hear a free Bitcoin fact?")
                    reprompt = "Hey, little novice, wanna hear a Bitcoin fact?"

                if purchase_result == PurchaseResult.DECLINED.value:

                    if purchasable == PurchasableState.PURCHASABLE:
                        speech = ("You don't currently own the Premium Legends pack, thus you cannot be called a Bitcoin guru!... So, my sweet apprentice, how about a free Bitcoin fact?")

                    else:
                        speech = get_random_yes_no_question()

                    reprompt = get_random_yes_no_question()

                return handler_input.response_builder.speak(speech).ask(reprompt).response

            else:
                logger.log("Connections.Response indicated failure. Error: {}".format(
                    handler_input.request_envelope.request.status.message))

                return handler_input.response_builder.speak(
                        "There was an error handling your cancellation "
                        "request. Please try again or contact us for help").response

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for help message to users."""
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HelpIntentHandler")
        in_skill_response = in_skill_product_response(handler_input)
        #category_product = [l for l in in_skill_response.in_skill_products if l.reference_name == "{}_pack".format(fact_category)]

        if isinstance(in_skill_response, InSkillProductsResponse):
            helps = ["Well, my little crypto friend, you have basically <prosody volume='loud'>two</prosody> options here. First, you can check out the 20 basic facts, that anyone should know about <prosody volume='loud'>Bit</prosody>coin. To do that, simply say, 'Tell me a fact' and it's yours. Next, if you already purchased the <prosody volume='loud'>Legends</prosody> pack, just say, 'Tell me a legend'. So, what's your choice?",
                     "Well, my dear crypto amigo, you have <prosody volume='loud'>two</prosody> options at this point. First, you can get the 20 basic facts that anyone should know about <prosody volume='loud'>Bit</prosody>coin. To do that, just say, 'Tell me a fact' and it's yours. Otherwise, if you already upgraded to the <prosody volume='loud'>Legends</prosody> pack, just say, 'Tell me a legend'. So, how can I help?",
                     "Well, my lovely <prosody volume='loud'>Bit</prosody>coin geek, you have <prosody volume='loud'>two</prosody> options now. First, you can learn the 20 basic facts that anyone should know about <prosody volume='loud'>Bit</prosody>coin. To do that, say, 'Tell me a fact' and it's yours. Additionally, if you already bought the <prosody volume='loud'>Legends</prosody> pack, just say, 'Tell me a legend'. So, what's it gonna be?"]

            speech = (random.choice(helps))
            handler_input.attributes_manager.session_attributes["lastSpeech"] = speech

            nice_fallbacks = ["Excuse me, I was checking my portfolio. Can you say it again?",
                              "<say-as interpret-as='interjection'>Damn</say-as>, my <prosody volume='loud'>wallet</prosody>coin looks good! Can you repeat?",
                              "Sorry, I didn't get that. I was stacking satoshis. Can you rephrase?",
                              "Sorry, I got a text from Satoshi. Can you say that again?",
                              "Sorry, I was checking my <prosody volume='loud'>Bit</prosody>coin wallet. Please say that again.",
                              "I beg your pardon, I was checking the price of <prosody volume='loud'>Bit</prosody>coin. Come again?",
                              "Forgive me, I was texting this guy, Nakamoto. Say that again, please!",
                              "I'm sorry, I was buying some coins. Can you repeat?",
                              "Excuse me, Satoshi keeps calling me. Please repeat!",
                              "<prosody volume='loud'>Oups</prosody>, you caught me checking my <prosody volume='loud'>Bit</prosody>coin stack. Say that again, please!"]

            reprompt = random.choice(nice_fallbacks)

        else:
            logger.info("Error calling InSkillProducts API: {}".format(in_skill_response.message))
            speech = "Something went wrong in loading your purchase history."
            reprompt = speech

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for fallback intent.

    2018-July-12: AMAZON.FallbackIntent is currently available in all
    English locales. This handler will not be triggered except in that
    locale, so it can be safely deployed for any locale. More info
    on the fallback intent can be found here: https://developer.amazon.com/docs/custom-skills/standard-built-in-intents.html#fallback
    """
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")

        nice_fallbacks = ["Excuse me, I was checking my portfolio. Can you say it again?",
                          "<say-as interpret-as='interjection'>Damn</say-as>, my <prosody volume='loud'>wallet</prosody>coin looks so good! Can you repeat?",
                          "Sorry, I didn't get that. I was stacking satoshis. Can you rephrase?",
                          "Sorry, I got a text from Satoshi. Can you say that again?",
                          "Sorry, I was checking my <prosody volume='loud'>Bit</prosody>coin wallet. Please say that again.",
                          "I beg your pardon, I was checking the price of <prosody volume='loud'>Bit</prosody>coin. Come again?",
                          "Forgive me, I was texting this guy, Nakamoto. Say that again, please!",
                          "I'm sorry, I was buying some coins. Can you repeat?",
                          "Excuse me, Satoshi keeps calling me. Please repeat!",
                          "<prosody volume='loud'>Oups</prosody>, you caught me checking my <prosody volume='loud'>Bit</prosody>coin stack. Say that again, please!"]

        speech = random.choice(nice_fallbacks)

        reprompt = (
                "Sorry, I cannot help with that. I can help you with "
                "some free <prosody volume='loud'>Bit</prosody>coin facts though. "
                "To hear a <prosody volume='loud'>Bit</prosody>coin fact you can say, "
                "'Tell me a fact', or to hear about the superstar level, say, 'What can I buy'. For help, say, "
                "'Help me'... So, how can I assist?"
            )

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedHandler(AbstractRequestHandler):
    """Handler for session end request, stop or cancel intents."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_request_type("SessionEndedRequest")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input) or
                is_intent_name("AMAZON.CancelIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SessionEndedHandler")
        global counter_facts
        global counter_legends
        counter_facts = []
        counter_legends = []
        return handler_input.response_builder.speak(get_random_goodbye()).set_should_end_session(True).response

class CatchAllExceptionHandler(AbstractExceptionHandler):
    """One exception handler to catch all exceptions."""
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        sorrys = ["Sorry, I can't understand the command. Please try again!",
                  "I'm not sure I understand your wish. Say it again! I'm all ears.",
                  "I didn't catch that. Can you repeat, please?"]

        speech = random.choice(sorrys)

        handler_input.response_builder.speak(speech).ask(speech)

        return handler_input.response_builder.response

class RequestLogger(AbstractRequestInterceptor):
    """Log the request envelope."""
    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.info("Request Envelope: {}".format(handler_input.request_envelope))

class ResponseLogger(AbstractResponseInterceptor):
    """Log the response envelope."""
    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.info("Response: {}".format(response))


sb = StandardSkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GetFactHandler())
sb.add_request_handler(YesHandler())
sb.add_request_handler(NoHandler())
sb.add_request_handler(GetCategoryFactHandler())
sb.add_request_handler(BuyResponseHandler())
sb.add_request_handler(CancelResponseHandler())
sb.add_request_handler(UpsellResponseHandler())
sb.add_request_handler(ShoppingHandler())
sb.add_request_handler(ProductDetailHandler())
sb.add_request_handler(BuyHandler())
sb.add_request_handler(CancelSubscriptionHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedHandler())
sb.add_request_handler(RepeatHandler())
sb.add_request_handler(WhatDidIBuyHandler())

sb.add_exception_handler(CatchAllExceptionHandler())
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

lambda_handler = sb.lambda_handler()

#End of program
