Example1_CreateProtocolFile=r"""
### EXAMPLE 1
INPUT:
Protocol1:

    A -> B : aenc( <'Hello', timestamp>, prA )
    B -> A : aenc( <n, timestamp>, prB )
    A -> B : < n+1, aenc(n, prA) >
    B -> A : < n+2, aenc(n, prB) >

Properties:
Secrecy of n:
    "All alice bob nonce #t1 .
        Exchange_Completed(alice, bob, nonce) @ #t1
        ==> not (Ex #t2 . K(nonce) @ #t2)"
    
Anti_Replay:
    "All alice bob nonce1 nonce2 #t1 #t2 .
        (Exchange_Completed(alice, bob, nonce1) @ #t1 &
        Exchange_Completed(alice, bob, nonce2) @ #t2 &
        nonce1 = nonce2)
        ==>
        #t1 = #t2"


EXPECTED OUTPUT:

theory ProtocolOne
begin

builtins: asymmetric-encryption
functions: succ/1

rule Create_Client :
    let
        pub = pk(~pr)
    in
    [
        Fr(~pr)
    ]
    -->
    [
        !Client($ClientName, ~pr, pub),
        Out(pub)
    ]

rule Alice_Initiates_Exchange :
    [
        Fr(~t),
        !Client(Alice, prA, pubA),
        !Client(Bob, prB, pubB)
    ]
    --[ Alice_Initiated_Exchange(Alice, Bob, ~t) ]->
    [
        Out(aenc(<'Hello', ~t>, prA)),
        Alice_Sent_Hello(Alice, ~t)
    ]


rule Bob_Sends_Nonce [derivchecks] :
    [
        !Client(Alice, prA, pubA),
        !Client(Bob, prB, pubB),
        In(aenc(<'Hello', t>, prA)),
        Fr(~n)
    ]
    --[ Bob_Received_Hello(Bob, t), Nonce(Alice, Bob, ~n) ]->
    [
        Out(aenc(<~n, t>, prB)),
        Bob_Sent_Nonce(Bob, ~n)
    ]

rule Alice_Receives_Nonce [derivchecks]:
    [
        !Client(Alice, prA, pubA),
        !Client(Bob, prB, pubB),
        Alice_Sent_Hello(Alice, t),
        In(aenc(<~n, t>, prB))
    ]
    -->
    [
        Out(<succ(~n), aenc(~n, prA)>),
        Alice_Answered_Nonce(Alice, ~n)
    ]

rule Bob_Answers_Nonce :
    [
        !Client(Alice, prA, pubA),
        !Client(Bob, prB, pubB),
        Bob_Sent_Nonce(Bob, ~n),
        In(<succ(~n), aenc(~n, prA)>)
    ]
    -->
    [
        Out(<succ(succ(~n)), aenc(~n, prB)>)
    ]

rule Alice_Concludes_Exchange :
    [
        !Client(Bob, prB, pubB),
        Alice_Answered_Nonce(Alice, ~n),
        In(<succ(succ(~n)), aenc(~n, prB)>)
    ]
    --[ Exchange_Completed(Alice, Bob, succ(~n)) ]->
    [ ]

restriction Bob_Checks_Timestamps : 
    "All bob t #t1 #t2 .
        Bob_Received_Hello(bob, t) @ #t1 &
        Bob_Received_Hello(bob, t) @ #t2
        ==> #t1 = #t2"

/*
lemma Sanity :
    exists-trace 
    "Ex alice bob nonce #t . Exchange_Completed(alice, bob, nonce) @ #t"
*/

lemma Secrecy :
    "All alice bob nonce #t1 .
        Exchange_Completed(alice, bob, nonce) @ #t1
        ==> not (Ex #t2 . K(nonce) @ #t2)"
    
lemma Anti_Replay :
    "All alice bob nonce1 nonce2 #t1 #t2 .
        (Exchange_Completed(alice, bob, nonce1) @ #t1 &
        Exchange_Completed(alice, bob, nonce2) @ #t2 &
        nonce1 = nonce2)
        ==>
        #t1 = #t2"
end

"""

Example2_CreateProtocolFile=r"""
### EXAMPLE 2
INPUT:  
Protocol Two:
    S -> C: h(M)
    C -> S: aenc_{pk(S)}(M)

Types:
    Agents: C, S
    Number: M
    Function: pk, h, inv.
        
Knowledge: 
    C: C, S, pk, h
    S: C, S, h, pk, inv(pk(S))  

Further Explanation:
    M is a message from A.
    aenc_{ k }(M) is an asymmetric encryption primitive that encrypts message M with key K.
    h is a hash function.

Properties:
Client_session_key_secrecy:
            " /* It cannot be that a  */
            not(
                Ex S k #i #j.
                    /* client has set up a session key 'k' with a server'S' */
                    SessKeyC(S, k) @ #i
                    /* and the adversary knows 'k' */
                    & K(k) @ #j
                    /* without having performed a long-term key reveal on 'S'. */
                    & not(Ex #r. LtkReveal(S) @ r)
                )
            "
Client_auth:
            " /* For all session keys 'k' setup by clients with a server 'S' */
                ( All S k #i.  SessKeyC(S, k) @ #i
                    ==>
                    /* there is a server that answered the request */
                    ( (Ex #a. AnswerRequest(S, k) @ a)
                    /* or the adversary performed a long-term key reveal on 'S'
                    before the key was setup. */
                    | (Ex #r. LtkReveal(S) @ r & r < i)
                    )
                )
            "

EXPECTED OUTPUT:

theory Protocol2

        begin

        builtins: asymmetric-encryption, hashing

        // Register a new asymmetric key pair for a public client A
        rule Register_pk:
            [ Fr(~ltk) ]
            -->
            [ !Ltk($A, ~ltk), !Pk($A, pk(~ltk)) ]

        // Make public keys available
        rule Get_pk:
            [ !Pk(A, pubkey) ]
            -->
            [ Out(pubkey) ]

        // Allow the attacker to have access to a compromised client's credentials
        rule Reveal_ltk:
            [ !Ltk(A, ltk) ]
            --[ LtkReveal(A) ]->
            [ Out(ltk) ]

        // Start a new thread executing the client role, choosing the server
        // non-deterministically.
        rule Client_1:
            [ Fr(~k)         // choose fresh key
            , !Pk($S, pkS)   // lookup public-key of server
            ]
        -->
            [ Client_1( $S, ~k )    // Store server and key for next step of thread
            , Out( aenc(~k, pkS) )  // Send the encrypted session key to the server
            ]

        rule Client_2:
            [ Client_1(S, k)   // Retrieve server and session key from previous step
            , In( h(k) )       // Receive hashed session key from network
            ]
        --[ SessKeyC( S, k ) ]-> // State that the session key 'k'
            []                     // was setup with server 'S'

        // A server thread answering in one-step to a session-key setup request from
        // some client.
        rule Serv_1:
            [ !Ltk($S, ~ltkS)                             // lookup the private-key
            , In( request )                               // receive a request
            ]
        --[ AnswerRequest($S, adec(request, ~ltkS)) ]-> // Explanation below
            [ Out( h(adec(request, ~ltkS)) ) ]            // Return the hash of the
                                                        // decrypted request

        lemma Client_session_key_secrecy:
            " /* It cannot be that a  */
            not(
                Ex S k #i #j.
                    /* client has set up a session key 'k' with a server'S' */
                    SessKeyC(S, k) @ #i
                    /* and the adversary knows 'k' */
                    & K(k) @ #j
                    /* without having performed a long-term key reveal on 'S'. */
                    & not(Ex #r. LtkReveal(S) @ r)
                )
            "

        lemma Client_auth:
            " /* For all session keys 'k' setup by clients with a server 'S' */
                ( All S k #i.  SessKeyC(S, k) @ #i
                    ==>
                    /* there is a server that answered the request */
                    ( (Ex #a. AnswerRequest(S, k) @ a)
                    /* or the adversary performed a long-term key reveal on 'S'
                    before the key was setup. */
                    | (Ex #r. LtkReveal(S) @ r & r < i)
                    )
                )
            "

        end 
"""

Example3_CreateProtocolFile = r"""
### EXAMPLE 3
INPUT:
Protocol ex_nine:

Knowledge:
    A: B, M1, K(A, B);
    B: A, M2, K(A, B);

Actions:
    [msg1] A -> B (Na) : Na;
    [msg2] B -> A (Nb) : Nb;
    [msg3] A -> B : xor(Na, K(A,B)) . senc{xor(M1, Na)}K(A,B);
    [msg4] B -> A : xor(Nb, K(A,B)) . senc{xor(M2, Nb)}K(A,B);
    [msg5] A -> B : senc{xor(xor(Na,  Nb),M1)}K(A,B);
    [msg6] B -> A : senc{xor(xor(Nb, Na), M2)}K(A,B);

end

EXPECTED OUTPUT:
theory ex_nine
begin

functions: pk/1, sk/1, aenc/2, adec/2

builtins: hashing

equations:
    adec(aenc(x.1, sk(x.2)), pk(x.2)) = x.1,
    adec(aenc(x.1, pk(x.2)), sk(x.2)) = x.1

rule Asymmetric_key_setup:
    [ Fr(~f) ] --> [ !Sk($A, sk(~f)), !Pk($A, pk(~f)) ]

rule Publish_public_keys:
    [ !Pk(A, pkA) ] --> [ Out(pkA) ]

rule Init_Knowledge:
        [ !Pk($C, pk(k_C)),
          !Pk($R, pk(k_R)),
          !Sk($C, sk(k_C)),
          !Sk($R, sk(k_R))
        ]
        --[  ]->
        [ St_init_C($C, sk(k_C), pk(k_C), pk(k_R)),
          St_init_R($R, sk(k_R), pk(k_R))
        ]

// ROLE C
rule cr1_C:
        [ St_init_C(C, sk(k_C), pk(k_C), pk(k_R)),
          Fr(~n)
        ]
        --[  ]->
        [ Out(aenc{~n}pk(k_R)),
          St_cr1_C(C, ~n, sk(k_C), pk(k_C), pk(k_R))
        ]

rule cr2_C:
        [ St_cr1_C(C, n, sk(k_C), pk(k_C), pk(k_R)),
          In(h(n))
        ]
        --[ Secret_n_secret_C(n),
            Secret_n_secretC_C(n),
            Commit_authNonInj(n),
            Commit_authInj(n) ]->
        [ St_cr2_C(C, n, sk(k_C), pk(k_C), pk(k_R))
        ]

// ROLE R
rule cr1_R:
        [ St_init_R(R, sk(k_R), pk(k_R)),
          In(aenc{n}pk(k_R))
        ]
        --[ Running_authNonInj(n),
            Running_authInj(n) ]->
        [ St_cr1_R(R, n, sk(k_R), pk(k_R))
        ]

rule cr2_R:
        [ St_cr1_R(R, n, sk(k_R), pk(k_R))
        ]
        --[ Secret_n_secret_R(n),
            Secret_n_secretR_R(n) ]->
        [ Out(h(n)),
          St_cr2_R(R, n, sk(k_R), pk(k_R))
        ]

lemma n_secret:
    " 
    not(
        Ex msg #i1 #i2 #j .
            Secret_n_secret_C(msg) @ #i1 &
            Secret_n_secret_R(msg) @ #i2 &
            K(msg) @ #j
    )"

lemma n_secretC:
    " not(
        Ex msg #i1 #j .
            Secret_n_secretC_C(msg) @ #i1 &
            K(msg) @ #j
    )"

lemma n_secretR:
    " not(
        Ex msg #i1 #j .
            Secret_n_secretR_R(msg) @ #i1 &
            K(msg) @ #j
    )"

lemma authNonInj:
    " (All m1 #i .
        Commit_authNonInj(m1)@ #i
        ==>
        (Ex #j . Running_authNonInj(m1) @ #j & #j < #i)
    )"


lemma authInj:
    " (All m1 #i .
        Commit_authInj(m1)@ #i
        ==>
        (Ex #j . Running_authInj(m1) @ #j & #j < #i) &
        (not (Ex #j . Commit_authInj(m1) @ #j & not (#i = #j)))
    )"
end
"""

Example4_CreateProtocolFile = r"""
### EXAMPLE 4
A CORRECT OUTPUT:
theory DIFFIE_HELLMAN
begin

functions: pk/1, sk/1, aenc/2, adec/2, g/0

builtins: diffie-hellman, symmetric-encryption

equations:
    adec(aenc(x.1, sk(x.2)), pk(x.2)) = x.1,
    adec(aenc(x.1, pk(x.2)), sk(x.2)) = x.1

rule Asymmetric_key_setup:
    [ Fr(~f) ] --> [ !Sk($A, sk(~f)), !Pk($A, pk(~f)) ]

rule Publish_public_keys:
    [ !Pk(A, pkA) ] --> [ Out(pkA) ]

rule Symmetric_key_setup:
    [ Fr(~symK) ] --> [ !Key($A, $B, ~symK) ]

rule Init_Knowledge:
        [ !Pk($A, pk(k_A)),
          !Pk($B, pk(k_B)),
          !Sk($A, sk(k_A)),
          !Sk($B, sk(k_B))
        ]
        --[  ]->
        [ St_init_A($A, sk(k_A), pk(k_A)),
          St_init_B($B, sk(k_B), pk(k_B))
        ]

// ROLE A
rule dh_1_A:
        [ St_init_A(A, sk(k_A), pk(k_A)),
          Fr(~x)
        ]
        --[  ]->
        [ Out((g() ^ ~x)),
          St_dh_1_A(A, ~x, sk(k_A), pk(k_A))
        ]

rule dh_2_A:
        [ St_dh_1_A(A, x, sk(k_A), pk(k_A)),
          In(alpha)
        ]
        --[  ]->
        [ St_dh_2_A(A, x, sk(k_A), pk(k_A), alpha)
        ]

rule dh_3_A:
        [ St_dh_2_A(A, x, sk(k_A), pk(k_A), alpha),
          Fr(~n)
        ]
        --[ Secret_key_secret_A((alpha ^ x)),
            Secret_key_secretA_A((alpha ^ x)) ]->
        [ Out(senc{~n}(alpha ^ x)),
          St_dh_3_A(A, ~n, x, sk(k_A), pk(k_A), alpha)
        ]

// ROLE B
rule dh_1_B:
        [ St_init_B(B, sk(k_B), pk(k_B)),
          In(alpha)
        ]
        --[  ]->
        [ St_dh_1_B(B, sk(k_B), pk(k_B), alpha)
        ]

rule dh_2_B:
        [ St_dh_1_B(B, sk(k_B), pk(k_B), alpha),
          Fr(~y)
        ]
        --[  ]->
        [ Out((g() ^ ~y)),
          St_dh_2_B(B, ~y, sk(k_B), pk(k_B), alpha)
        ]

rule dh_3_B:
        [ St_dh_2_B(B, y, sk(k_B), pk(k_B), alpha),
          In(senc{n}(alpha ^ y))
        ]
        --[ Secret_key_secret_B((alpha ^ y)),
            Secret_key_secretB_B((alpha ^ y)) ]->
        [ St_dh_3_B(B, n, y, sk(k_B), pk(k_B), alpha)
        ]

lemma key_secret:
    " not(
        Ex msg #i1 #i2 #j .
            Secret_key_secret_A(msg) @ #i1 &
            Secret_key_secret_B(msg) @ #i2 &
            K(msg) @ #j
    )"

end
"""

Example5_CreateProtocolFile = r"""
### EXAMPLE 5
INPUT:
Protocol ex_eight:

Declarations:
    xor/2;

Knowledge:
    A: B, C,  K(A,B), M;
    B: A, C,  K(A,B),  K(B,C);
    C: A, B,  K(B,C);

Actions:
    [m1] A -> B (Na): Na . A . C;
    [m2] B -> C (Nb): xor(Na ,  K(B,C)) . Nb;
    [m3] C -> B (Nc): xor(Nb ,  K(B,C)) . Nc;
    [m4] B -> A : xor(Nc ,  K(A,B)) . xor(xor(xor( Na , Nb ) , Nc) ,  K(A,B));
    [m5] A -> B : senc{xor(xor(M , Na) , xor(Nc ,  K(A,B)))} K(A,B);
    [m6] B -> C : senc{xor(xor(M , Na) , xor(Nc ,  K(A,B)))} K(B,C);
end

# Failed properties
-  Secrecy of K1
-  Secrecy of K2
-  Secrecy of M

EXPECTED OUTPUT:

theory ex_eight
begin

functions: pk/1, sk/1, aenc/2, adec/2

builtins: symmetric-encryption, xor

equations:
    adec(aenc(x.1, sk(x.2)), pk(x.2)) = x.1,
    adec(aenc(x.1, pk(x.2)), sk(x.2)) = x.1

rule Asymmetric_key_setup:
    [ Fr(~f) ] --> [ !Sk($A, sk(~f)), !Pk($A, pk(~f)) ]

rule Publish_public_keys:
    [ !Pk(A, pkA) ] --> [ Out(pkA) ]

rule Symmetric_key_setup:
    [ Fr(~symK) ] --> [ !Key($A, $B, ~symK) ]

rule Init_Knowledge:
        [ !Key($A, $B, k_A_B),
          !Key($B, $C, k_B_C),
          !Pk($A, pk(k_A)),
          !Pk($B, pk(k_B)),
          !Pk($C, pk(k_C)),
          !Sk($A, sk(k_A)),
          !Sk($B, sk(k_B)),
          !Sk($C, sk(k_C)),
          Fr(~M)
        ]
        --[  ]->
        [ St_init_A($A, $B, $C, ~M, sk(k_A), pk(k_A), k_A_B),
          St_init_B($A, $B, $C, sk(k_B), pk(k_B), k_A_B, k_B_C),
          St_init_C($A, $B, $C, sk(k_C), pk(k_C), k_B_C)
        ]

// ROLE A
rule m1_A:
        [ St_init_A(A, B, C, M, sk(k_A), pk(k_A), k_A_B),
          Fr(~Na)
        ]
        --[  ]->
        [ Out(<~Na, A, C>),
          St_m1_A(A, B, C, M, ~Na, sk(k_A), pk(k_A), k_A_B)
        ]

rule m4_A:
        [ St_m1_A(A, B, C, M, Na, sk(k_A), pk(k_A), k_A_B),
          In(<alpha, beta>)
        ]
        --[  ]->
        [ St_m4_A(A, B, C, M, Na, sk(k_A), pk(k_A), k_A_B, alpha, beta)
        ]

rule m5_A:
        [ St_m4_A(A, B, C, M, Na, sk(k_A), pk(k_A), k_A_B, alpha, beta)
        ]
        --[ SecretM(M) ]->
        [ Out(senc{M XOR Na XOR alpha}k_A_B),
          St_m5_A(A, B, C, M, Na, sk(k_A), pk(k_A), k_A_B, alpha, beta)
        ]

// ROLE B
rule m1_B:
        [ St_init_B(A, B, C, sk(k_B), pk(k_B), k_A_B, k_B_C),
          In(<Na, A, C>)
        ]
        --[  ]->
        [ St_m1_B(A, B, C, Na, sk(k_B), pk(k_B), k_A_B, k_B_C)
        ]

rule m2_B:
        [ St_m1_B(A, B, C, Na, sk(k_B), pk(k_B), k_A_B, k_B_C),
          Fr(~Nb)
        ]
        --[  Secret2(k_B_C) ]->
        [ Out(<Na XOR k_B_C, ~Nb>),
          St_m2_B(A, B, C, Na, ~Nb, sk(k_B), pk(k_B), k_A_B, k_B_C)
        ]

rule m3_B:
        [ St_m2_B(A, B, C, Na, Nb, sk(k_B), pk(k_B), k_A_B, k_B_C),
          In(<Nb XOR k_B_C, Nc>)
        ]
        --[ ]->
        [ St_m3_B(A, B, C, Na, Nb, Nc, sk(k_B), pk(k_B), k_A_B, k_B_C)
        ]

rule m4_B:
        [ St_m3_B(A, B, C, Na, Nb, Nc, sk(k_B), pk(k_B), k_A_B, k_B_C)
        ]
        --[  Secret1(k_A_B) ]->
        [ Out(<Nc XOR k_A_B, Na XOR Nb XOR Nc, k_A_B>),
          St_m4_B(A, B, C, Na, Nb, Nc, sk(k_B), pk(k_B), k_A_B, k_B_C)
        ]

rule m5_B:
        [ St_m4_B(A, B, C, Na, Nb, Nc, sk(k_B), pk(k_B), k_A_B, k_B_C),
          In(senc{beta}k_A_B)
        ]
        --[  ]->
        [ St_m5_B(A, B, C, Na, Nb, Nc, sk(k_B), pk(k_B), k_A_B, k_B_C, beta)
        ]

rule m6_B:
        [ St_m5_B(A, B, C, Na, Nb, Nc, sk(k_B), pk(k_B), k_A_B, k_B_C, beta)
        ]
        --[  ]->
        [ Out(senc{beta}k_B_C),
          St_m6_B(A, B, C, Na, Nb, Nc, sk(k_B), pk(k_B), k_A_B, k_B_C, beta)
        ]

// ROLE C
rule m2_C:
        [ St_init_C(A, B, C, sk(k_C), pk(k_C), k_B_C),
          In(<alpha, Nb>)
        ]
        --[  ]->
        [ St_m2_C(A, B, C, Nb, sk(k_C), pk(k_C), k_B_C, alpha)
        ]

rule m3_C:
        [ St_m2_C(A, B, C, Nb, sk(k_C), pk(k_C), k_B_C, alpha),
          Fr(~Nc)
        ]
        --[ Secret2(n) ]->
        [ Out(<Nb XOR k_B_C, ~Nc>),
          St_m3_C(A, B, C, Nb, ~Nc, sk(k_C), pk(k_C), k_B_C, alpha)
        ]

rule m6_C:
        [ St_m3_C(A, B, C, Nb, Nc, sk(k_C), pk(k_C), k_B_C, alpha),
          In(senc{beta}k_B_C)
        ]
        --[  Execute_m6_C(M)]->
        [ St_m6_C(A, B, C, Nb, Nc, sk(k_C), pk(k_C), k_B_C, alpha, beta)
        ]


//execution
lemma executable:
exists-trace
"
Ex M #i . Execute_m6_C(M) @ #i
"

// Secrecy of K(A,B)
lemma secrecy_K1:
    all-traces
    "All n #i. Secret1(n) @i ==> (not (Ex #j. K(n)@j))"

// Secrecy of K(B, C)
lemma secrecy_K2:
    all-traces
    "All n #i. Secret2(n) @i ==> (not (Ex #j. K(n)@j))"

// Secrecy of M
lemma secrecy_M:
    all-traces
    "All m #i. SecretM(m) @i ==> (not (Ex #j. K(m)@j))"

// NB: Tamarin loops in precomputation
end
"""




Example1_FormalizingTool=r"""
### Example 1:
Protocol ASW: 
Knowledge: 
    A : m, pk(B), B; 
    B : pk(A), A; 
    
Actions: 
    [asw1] A -> B (n_1) : aenc{ pk(A) . pk(B) . m . h(n_1) }sk(A); 
    [asw2] B -> A (n_2) : aenc{ aenc{ pk(A) . pk(B) . m . h(n_1)}sk(A) . h(n_2) }sk(B); 
    [asw3] A -> B : n_1; 
    [asw4] B -> A : n_2;     
end

Explanation:
- n_1, n_2 are nonces generated freshly by A and B respectively;
- pk(A) and pk(B) are public keys of A and B respectively.
"""

Example2_FormalizingTool=r"""
### Example 2:
Protocol DIFFIE_HELLMAN: 
Declarations:
    g/0;
    
Actions: 
    [dh_1] A -> B (x) : g()^x; 
    [dh_2] B -> A (y) : g()^y; 
    [dh_3] A -> B (n) : senc{ n }(g()^(x*y)); 
    
end

Explanation:
    - g is a defined 0-ary function;
    - x, y and n are nonces generated by A, B, A respectively;
    - ^ is the exponentiation;
    - * is the product.

"""

Example3_FormalizingTool=r"""
### Example 3:
Protocol four: 

Declarations : g/0;

Knowledge: 
    A : K1;
    B : K1; 
    
Actions: 
    [p1] A -> B (pra, N1) : g()^pra . N1;

    [p2] B -> A (prb, N2) : g()^prb . senc{ N1 }(g()^(pra*prb)) . N2;
    [p3] A -> B : senc{ N2 }(g()^(prb*pra));

Explanation:
    - pra and N1 are freshly generated by A in the first message p1;
    - prb and N2 are freshly generated by B in the second message p2;
    - g/0 is a define 0-ary function (a constant);
    - ^ is exponentiation while * is product

"""

Example4_FormalizingTool=r"""
### Example 4
Protocol six:
Declarations:
xor/2;

Knowledge:
    A: B, C, k(A, C);
    B: A, C, k(B, C);
    C: A, B, k(A, C), k(B, C);

Actions:
    [m1] A -> C (Na): A . B . Na;
    [m2] C -> A (Ks): senc{Na . K(B,C) . B}K(A, C) . senc{senc{Ks . A}K(B,C)}K(A, C);
    [m3] A -> B : senc{Ks . A}K(B,C);
    [m4] B -> A (Nb): senc{Nb}Ks;
    [m5] A -> B : senc{h(Nb)} Ks;
end

EXPLANATION:
    - k(A,C), k(B, C) are symmetric shared keys;
    - xor/2 is a declared binary function (the tool doesn't support xor);
    - Na, Ks, Nb are freshly generated by A, C, B on messages m1, m2, m4 respectively;
    - Ks is used as a symmetric key on m4 and m5;
    - h(Nb) is the application of the hash function on the nonce Nb.
"""

Example5_FormalizingTool=r"""
### Example 5

Protocol NSLPKthree:
Knowledge: 
    I : pk(R);
    R : pk(I);
    
Actions: 
    [msg1] I -> R (ni) : aenc{ 'one' . ni . I }pk(R);
    [msg2] R -> I (nr) : aenc{ 'two' . ni . nr . R }pk(I);
    [msg3] I -> R : aenc{ 'three' . nr }pk(R);
end

"""

Example1_ConfrontAndFix = r"""
### Example 1
**Original protocol:**
Protocol ex_eight:

Declarations:
xor/2;

Knowledge:
A: B, C,  K(A,B), M;
B: A, C,  K(A,B),  K(B,C);
C: A, B,  K(B,C);

Actions:
[m1] A -> B (Na): Na . A . C;
[m2] B -> C (Nb): xor(Na ,  K(B,C)) . Nb;
[m3] C -> B (Nc): xor(Nb ,  K(B,C)) . Nc;
[m4] B -> A : xor(Nc ,  K(A,B)) . xor(xor(xor( Na , Nb ) , Nc) ,  K(A,B));
[m5] A -> B : senc{xor(xor(M , Na) , xor(Nc ,  K(A,B)))} K(A,B);
[m6] B -> C : senc{xor(xor(M , Na) , xor(Nc ,  K(A,B)))} K(B,C);
end

# Failed properties

-  Secrecy of K1
-  Secrecy of K2
-  Secrecy of M

**A Good Output:**
theory ex_eight
begin

functions: pk/1, sk/1, aenc/2, adec/2

builtins: symmetric-encryption, xor

equations:
    adec(aenc(x.1, sk(x.2)), pk(x.2)) = x.1,
    adec(aenc(x.1, pk(x.2)), sk(x.2)) = x.1

rule Asymmetric_key_setup:
    [ Fr(~f) ] --> [ !Sk($A, sk(~f)), !Pk($A, pk(~f)) ]

rule Publish_public_keys:
    [ !Pk(A, pkA) ] --> [ Out(pkA) ]

rule Symmetric_key_setup:
    [ Fr(~symK) ] --> [ !Key($A, $B, ~symK) ]

rule Init_Knowledge:
        [ !Key($A, $B, k_A_B),
          !Key($B, $C, k_B_C),
          !Pk($A, pk(k_A)),
          !Pk($B, pk(k_B)),
          !Pk($C, pk(k_C)),
          !Sk($A, sk(k_A)),
          !Sk($B, sk(k_B)),
          !Sk($C, sk(k_C)),
          Fr(~M)
        ]
        --[  ]->
        [ St_init_A($A, $B, $C, ~M, sk(k_A), pk(k_A), k_A_B),
          St_init_B($A, $B, $C, sk(k_B), pk(k_B), k_A_B, k_B_C),
          St_init_C($A, $B, $C, sk(k_C), pk(k_C), k_B_C)
        ]

// ROLE A
rule m1_A:
        [ St_init_A(A, B, C, M, sk(k_A), pk(k_A), k_A_B),
          Fr(~Na)
        ]
        --[  ]->
        [ Out(<~Na, A, C>),
          St_m1_A(A, B, C, M, ~Na, sk(k_A), pk(k_A), k_A_B)
        ]

rule m4_A:
        [ St_m1_A(A, B, C, M, Na, sk(k_A), pk(k_A), k_A_B),
          In(<alpha, beta>)
        ]
        --[  ]->
        [ St_m4_A(A, B, C, M, Na, sk(k_A), pk(k_A), k_A_B, alpha, beta)
        ]

rule m5_A:
        [ St_m4_A(A, B, C, M, Na, sk(k_A), pk(k_A), k_A_B, alpha, beta)
        ]
        --[ SecretM(M) ]->
        [ Out(senc{M XOR Na XOR alpha}k_A_B),
          St_m5_A(A, B, C, M, Na, sk(k_A), pk(k_A), k_A_B, alpha, beta)
        ]

// ROLE B
rule m1_B:
        [ St_init_B(A, B, C, sk(k_B), pk(k_B), k_A_B, k_B_C),
          In(<Na, A, C>)
        ]
        --[  ]->
        [ St_m1_B(A, B, C, Na, sk(k_B), pk(k_B), k_A_B, k_B_C)
        ]

rule m2_B:
        [ St_m1_B(A, B, C, Na, sk(k_B), pk(k_B), k_A_B, k_B_C),
          Fr(~Nb)
        ]
        --[  Secret2(k_B_C) ]->
        [ Out(<Na XOR k_B_C, ~Nb>),
          St_m2_B(A, B, C, Na, ~Nb, sk(k_B), pk(k_B), k_A_B, k_B_C)
        ]

rule m3_B:
        [ St_m2_B(A, B, C, Na, Nb, sk(k_B), pk(k_B), k_A_B, k_B_C),
          In(<Nb XOR k_B_C, Nc>)
        ]
        --[ ]->
        [ St_m3_B(A, B, C, Na, Nb, Nc, sk(k_B), pk(k_B), k_A_B, k_B_C)
        ]

rule m4_B:
        [ St_m3_B(A, B, C, Na, Nb, Nc, sk(k_B), pk(k_B), k_A_B, k_B_C)
        ]
        --[  Secret1(k_A_B) ]->
        [ Out(<Nc XOR k_A_B, Na XOR Nb XOR Nc, k_A_B>),
          St_m4_B(A, B, C, Na, Nb, Nc, sk(k_B), pk(k_B), k_A_B, k_B_C)
        ]

rule m5_B:
        [ St_m4_B(A, B, C, Na, Nb, Nc, sk(k_B), pk(k_B), k_A_B, k_B_C),
          In(senc{beta}k_A_B)
        ]
        --[  ]->
        [ St_m5_B(A, B, C, Na, Nb, Nc, sk(k_B), pk(k_B), k_A_B, k_B_C, beta)
        ]

rule m6_B:
        [ St_m5_B(A, B, C, Na, Nb, Nc, sk(k_B), pk(k_B), k_A_B, k_B_C, beta)
        ]
        --[  ]->
        [ Out(senc{beta}k_B_C),
          St_m6_B(A, B, C, Na, Nb, Nc, sk(k_B), pk(k_B), k_A_B, k_B_C, beta)
        ]

// ROLE C
rule m2_C:
        [ St_init_C(A, B, C, sk(k_C), pk(k_C), k_B_C),
          In(<alpha, Nb>)
        ]
        --[  ]->
        [ St_m2_C(A, B, C, Nb, sk(k_C), pk(k_C), k_B_C, alpha)
        ]

rule m3_C:
        [ St_m2_C(A, B, C, Nb, sk(k_C), pk(k_C), k_B_C, alpha),
          Fr(~Nc)
        ]
        --[ Secret2(n) ]->
        [ Out(<Nb XOR k_B_C, ~Nc>),
          St_m3_C(A, B, C, Nb, ~Nc, sk(k_C), pk(k_C), k_B_C, alpha)
        ]

rule m6_C:
        [ St_m3_C(A, B, C, Nb, Nc, sk(k_C), pk(k_C), k_B_C, alpha),
          In(senc{beta}k_B_C)
        ]
        --[  Execute_m6_C(M)]->
        [ St_m6_C(A, B, C, Nb, Nc, sk(k_C), pk(k_C), k_B_C, alpha, beta)
        ]


//execution
lemma executable:
exists-trace
"
Ex M #i . Execute_m6_C(M) @ #i
"

// Secrecy of K_A_B
lemma secrecy_K1:
    all-traces
    "All n #i. Secret1(n) @i ==> (not (Ex #j. K(n)@j))"

// Secrecy of K_B_C
lemma secrecy_K2:
    all-traces
    "All n #i. Secret2(n) @i ==> (not (Ex #j. K(n)@j))"

// Secrecy of M
lemma secrecy_M:
    all-traces
    "All m #i. SecretM(m) @i ==> (not (Ex #j. K(m)@j))"

end

"""

Example2_ConfrontAndFix = r"""
### Example 2
**Original Input Protocol:**
    protocol ex_seven
    Kac is a symmetric key preshared by A and C
    Kbc is a symmetric key preshared by B and C
    K is a symmetric key generated by C
    
    A -> C : A, B, Na
    C -> A : senc((Na, K, B), Kac), senc(senc((K, A), Kbc), Kac)
    A -> B : senc((K, A), Kbc)
    B -> A : senc(Nb, K)
    A -> B : senc(h(Nb), K)
    
    Freshness of K is not verified

**A good output:**
    theory ex_seven
    begin
    
    
    builtins: hashing, symmetric-encryption
    
    rule Symmetric_key_setup:
        [ Fr(~symK) ] --> [ !Key($A, $B, ~symK) ]
    
    rule Init_Knowledge:
            [ !Key($A, $C, k_A_C),
              !Key($B, $C, k_B_C)
            ]
            --[  ]->
            [ St_init_A($A, $B, $C,  k_A_C),
              St_init_C($A, $B, $C,  k_A_C, k_B_C),
              St_init_B($A, $B, $C,  k_B_C)
            ]
    
    // ROLE $A
    rule m1_A:
            [ St_init_A($A, $B, $C,  k_A_C),
              Fr(~Na)
            ]
            --[  ]->
            [ Out(<$A, $B, ~Na>),
              St_m1_A($A, $B, $C, ~Na,  k_A_C)
            ]
    
    //~Ks is fresh since gets ~Na back encrypted with k_A_C
    rule m2_A:
            [ St_m1_A($A, $B, $C, ~Na,  k_A_C),
              In(<senc{<~Na, ~Ks, $B>}k_A_C, senc{alpha}k_A_C>)
            ]
            --[In_m2_A(alpha)]->
            [ St_m2_A($A, $B, $C, ~Ks, ~Na,  k_A_C, alpha)
            ]
    
    rule m3_A:
            [ St_m2_A($A, $B, $C, Ks, ~Na,  k_A_C, alpha)
            ]
            --[  ]->
            [ Out(alpha),
              St_m3_A($A, $B, $C, Ks, ~Na,  k_A_C, alpha)
            ]
    
    rule m4_A:
            [ St_m3_A($A, $B, $C, Ks, ~Na,  k_A_C, alpha),
              In(senc{Nb}Ks)
            ]
            --[  ]->
            [ St_m4_A($A, $B, $C, Ks, ~Na, Nb,  k_A_C, alpha)
            ]
    
    rule m5_A:
            [ St_m4_A($A, $B, $C, Ks, Na, Nb,  k_A_C, alpha)
            ]
            --[  ]->
            [ Out(senc{h(Nb)}Ks),
              St_m5_A($A, $B, $C, Ks, Na, Nb,  k_A_C, alpha)
            ]
    
    // ROLE $C
    rule m1_C:
            [ St_init_C($A, $B, $C,  k_A_C, k_B_C),
              In(<$A, $B, Na>)
            ]
            --[  ]->
            [ St_m1_C($A, $B, $C, Na,  k_A_C, k_B_C)
            ]
    
    rule m2_C:
            [ St_m1_C($A, $B, $C, Na,  k_A_C, k_B_C),
              Fr(~Ks)
            ]
            --[ OUT_m2_C(senc{<~Ks, $A>}k_B_C)  ]->
            [ Out(<senc{<Na, ~Ks, $B>}k_A_C, senc{senc{<~Ks, $A>}k_B_C}k_A_C>),
              St_m2_C($A, $B, $C, ~Ks, Na,  k_A_C, k_B_C)
            ]
    
    // ROLE $B
    rule m3_B:
            [ St_init_B($A, $B, $C,  k_B_C),
              In(senc{<Ks, $A>}k_B_C)
            ]
            --[  ]->
            [ St_m3_B($A, $B, $C, Ks,  k_B_C)
            ]
    
    rule m4_B:
            [ St_m3_B($A, $B, $C, Ks,  k_B_C),
              Fr(~Nb)
            ]
            --[  ]->
            [ Out(senc{~Nb}Ks),
              St_m4_B($A, $B, $C, Ks, ~Nb,  k_B_C)
            ]
    
    rule m5_B:
            [ St_m4_B($A, $B, $C, Ks, Nb,  k_B_C),
              In(senc{h(Nb)}Ks)
            ]
            --[ Exchange_Completed(Ks) ]->
            [ St_m5_B($A, $B, $C, Ks, Nb,  k_B_C)
            ]
    
    lemma types [sources]:
    " 
    All alpha #i.
    In_m2_A(alpha) @ i
    ==>
    ( (Ex #j. KU(alpha) @ j & j < i)
    | (Ex #j. OUT_m2_C(alpha) @ j)
    )

    "
    
    lemma anti_replay:
    "
    All kf #t1 #t2 .
        (Exchange_Completed(kf) @ #t1 &
        Exchange_Completed(kf) @ #t2)
        ==>
        #t1 = #t2
    "
    end
    
"""

Example3_ConfrontAndFix = r"""
### Example 3
** Original Input Protocol:**
    Protocol nine_ex
    
    K is a preshared key between A and B
    Na is a nonce generated by A
    Nb is a nonce generated by B
    M1 is a message from A to B
    M2 is a message from B to A
    
    A -> B : Na
    B -> A : Nb
    A -> B : (Na xor K), senc((M1 xor Na), K)
    B -> A : (Nb xor K), senc((M2 xor Nb), K)
    A -> B : senc((Na xor Nb xor M1), K)
    B -> A : senc((Nb xor Na xor M2), K)
    
    # Failed properties
    
    -  Secrecy of M1
    -  Secrecy of M2

** A Good Output:**
    theory nine_ex
    begin
    
    functions:aenc/2, adec/2
    
    builtins: symmetric-encryption, xor
    predicates: Equality_check (gamma, Nb, Na, epsilon) <=> gamma ⊕ Nb =  Na ⊕ Nb ⊕ epsilon
    
    rule Symmetric_key_setup:
        [ Fr(~symK) ] --> [ !Key($A, $B, ~symK) ]
    
    rule Init_Knowledge:
            [ !Key($A, $B, k_A_B),
              Fr(~M1),
              Fr(~M2)
            ]
            --[  ]->
            [ St_init_A($A, $B, ~M1, k_A_B),
              St_init_B($A, $B, ~M2, k_A_B)
            ]
    
    // ROLE A
    rule msg1_A:
            [ St_init_A(A, B, M1, k_A_B),
              Fr(~Na)
            ]
            --[  First(~Na)]->
            [ Out(~Na),
              St_msg1_A(A, B, M1, ~Na, k_A_B)
            ]
    
    rule msg2_A:
            [ St_msg1_A(A, B, M1, ~Na, k_A_B),
              In(Nb)
            ]
            --[  ]->
            [ St_msg2_A(A, B, M1, ~Na, Nb, k_A_B)
            ]
    
    rule msg3_A:
            [ St_msg2_A(A, B, M1, ~Na, Nb, k_A_B)
            ]
            --[ OUT_m3_A((M1 ⊕ ~Na)) ]->
            [ Out(<(~Na ⊕ k_A_B), senc{(M1 ⊕ ~Na)}k_A_B>),
              St_msg3_A(A, B, M1, ~Na, Nb, k_A_B)
            ]
    
    
    rule msg4_A:
            [ St_msg3_A(A, B, M1, Na, Nb, k_A_B),
              In(<Nb ⊕ k_A_B, senc{gamma}k_A_B>)
            ]
            --[  In_m4_A(gamma)]->
            [ St_msg4_A(A, B, M1, Na, Nb, k_A_B, gamma)
            ]
    
    rule msg5_A:
            [ St_msg4_A(A, B, M1, Na, Nb, k_A_B, gamma)
            ]
            --[Secret1(M1), OUT_m5_A(senc{Na ⊕ Nb ⊕ M1}k_A_B) ]->
            [ Out(senc{Na ⊕ Nb ⊕ M1}k_A_B),
              St_msg5_A(A, B, M1, Na, Nb, k_A_B, gamma)
            ]
    
    rule msg6_A:
            let 
            gammaNb = gamma ⊕ Nb
            NaNbepsilon = Na ⊕ Nb ⊕ epsilon 
            in 
            [            
              St_msg5_A(A, B, M1, Na, Nb, k_A_B, gamma),
              In(senc{epsilon}k_A_B)
            ]
            --[ In_m6_A(epsilon), Equality_let(gammaNb, NaNbepsilon), Equality(gamma, Nb, Na, epsilon)]-> //_restrict(gamma ⊕ Nb =  Na ⊕ Nb ⊕ epsilon)  
            [ St_msg6_A(A, B, M1, Na, Nb, k_A_B, gamma, epsilon)
            ]
    // ROLE B
    rule msg1_B:
            [ St_init_B(A, B, M2, k_A_B),
              In(Na)
            ]
            --[  ]->
            [ St_msg1_B(A, B, M2, Na, k_A_B)
            ]
    
    rule msg2_B:
            [ St_msg1_B(A, B, M2, Na, k_A_B),
              Fr(~Nb)
            ]
            --[  ]->
            [ Out(~Nb),
              St_msg2_B(A, B, M2, Na, ~Nb, k_A_B)
            ]
    
    // beta is M1 xor NA
    rule msg3_B:
            [ St_msg2_B(A, B, M2, Na, Nb, k_A_B),
              In(<Na ⊕ k_A_B, senc{beta}k_A_B>)
            ]
            --[  In_m3_B(beta)]->
            [ St_msg3_B(A, B, M2, Na, Nb, k_A_B, beta)
            ]
    // gamma is M2 xor Nb
    rule msg4_B:
            [ St_msg3_B(A, B, M2, Na, Nb, k_A_B, beta)
            ]
            --[ OUT_m4_B(M2 ⊕ Nb) ]->
            [ Out(<Nb ⊕ k_A_B, senc{M2 ⊕ Nb}k_A_B>),
              St_msg4_B(A, B, M2, Na, Nb, k_A_B, beta)
            ]
    
    rule msg5_B:
            [
              St_msg4_B(A, B, M2, Na, Nb, k_A_B, beta),
              In(senc{delta}k_A_B),
            ]
            --[In_m5_B(senc{delta}k_A_B) ]->  //_restrict(beta ⊕ Na =  Nb ⊕ (Na ⊕ delta))
            [ St_msg5_B(A, B, M2, Na, Nb, k_A_B, beta, delta)
            ]
    
    rule msg6_B:
            [ St_msg5_B(A, B, M2, Na, Nb, k_A_B, beta, delta)
            ]
            --[  Secret2(M2), OUT_m6_B(Nb ⊕ Na ⊕ M2)]->
            [ Out(senc{Nb ⊕ Na ⊕ M2}k_A_B),
              St_msg6_B(A, B, M2, Na, Nb, k_A_B, beta, delta)
            ]
    
    // restriction restriction_equality_check:
    // "∀ g e #i. (Equality_let( g, e) @ #i) ⇒ g=e"
    
    restriction restriction_with_predicate:
    "∀ g  b  a  e  #i . Equality(g, b, a, e) @ #i ⇒ Equality_check(g,b,a,e) "
    
    lemma executable:
    exists-trace
    "Ex n m1 m2 #i1 #i2 #i3 . First(n) @ #i1 & Secret1(m1) @ #i2 & Secret2(m2) @ #i3" 
    
    lemma secrecy1:
    "All x #i.
    Secret1(x) @i ==> not (Ex #j. K(x)@j)"
    
    lemma secrecy2:
    "All x #i.
    Secret2(x) @i ==> not (Ex #j. K(x)@j)"
    
    end

"""


Example1_MyAttackTrace=r"""
### Example 1
Protocol ASW: 
    Knowledge: 
        A : m, pk(B), B; 
        B : pk(A), A; 
        
    Actions: 
        [asw1] A -> B (n_1) : 
            aenc{ pk(A) . pk(B) . m . h(n_1) }sk(A); 
        [asw2] B -> A (n_2) : 
            aenc{ aenc{pk(A) . pk(B) . m . h(n_1)}sk(A) . h(n_2) }sk(B); 
        [asw3] A -> B : 
            n_1; 
        [asw4] B -> A :
            n_2;
    
    lemma Secrecy :
      "not (Ex m #t1 #t2 . Secret(m)@#t1 & K(m)@#t2)"

Attack:
    A -> E : aenc{pkA, pkB, m, h(n.1)}skA;
"""

Example2_MyAttackTrace = r"""
### Example 2
**The AnB protocol**
Protocol OTWAY_REES: 

Knowledge: 
    A: k(A, S), B; 
    B: k(B, S); 
    S: k(A, S), k(B, S); 

Actions: 
    [or1] A -> B (n1, i) : 
        i . A . B . senc{n1 . i . A . B}k(A, S); 
    [or2] B -> S (n2) : 
        i . A . B . senc{n1 . i . A . B}k(A, S) . senc{n2 . i . A . B}k(B, S); 
    [or3] S -> B (key) : 
        i . senc{n1 . key}k(A, S) . senc{n2 . key}k(B, S); 
    [or4] B -> A : 
        i . senc{n1 . key}k(A, S); 

end

**The Expected AnB attack trace output**
Types:
	A : A;
	B : B;
	E : Attacker;
Actions:
	A -> E : i.1 . A . B . senc{n1 . i.1 . A . B}k(A,B);
	E -> A : i.1 . senc{n1 . i.1 . A . B}k(A,B);
"""

Example3_MyAttackTrace = r"""
**The AnB protocol**
    Protocol DIFFIE_HELLMAN:

    Declarations:
        g/0;

    Knowledge: 
        A : sec1, sec2;
        B : sec1, sec2;

    Actions: 
        [dh_1] A -> B (x) : sec1 . g()^x; 
        [dh_2] B -> A (y) : g()^y; 
        [dh_3] A -> B (key) : sec2 . senc{key}(g()^(x*y));
        [dh_4] B -> A (m) : senc{m}(key); 

    end

**The Expected AnB attack trace output**
    Types :
        A : A;
        B : B;
        E : Attacker;
    Actions:
        A -> E : sec1 . g()^x;
        E -> A : alpha;
        A -> E : sec2 . senc{key.1}(alpha^x);
        E -> B : sec1 . g();
        B -> E : g()^y;
        E -> B : sec2 . senc{key}(g()^y);
        B -> E : senc{m}key;

"""


Example1_TranslateTrace=r"""
### Example 1
**The AnB Protocol**

Protocol ASW: 

Knowledge: 
    A : m, pk(B), B; 
    B : pk(A), A; 
    
Actions: 
    [asw1] A -> B (n_1) : 
        aenc{ pk(A) . pk(B) . m . h(n_1) }sk(A); 
    [asw2] B -> A (n_2) : 
        aenc{ aenc{pk(A) . pk(B) . m . h(n_1)}sk(A) . h(n_2) }sk(B); 
    [asw3] A -> B : 
        n_1; 
    [asw4] B -> A :
        n_2;
end


**The Tamarin Protocol**

theory ASW
begin

functions: pk/1, sk/1, aenc/2, adec/2

builtins: hashing

equations:
    adec(aenc(x.1, sk(x.2)), pk(x.2)) = x.1,
    adec(aenc(x.1, pk(x.2)), sk(x.2)) = x.1

rule Asymmetric_key_setup:
    [ Fr(~f) ] --> [ !Sk($A, sk(~f)), !Pk($A, pk(~f)) ]

rule Publish_public_keys:
    [ !Pk(A, pkA) ] --> [ Out(pkA) ]

rule Init_Knowledge:
        [ !Pk($A, pk(k_A)),
          !Pk($B, pk(k_B)),
          !Sk($A, sk(k_A)),
          !Sk($B, sk(k_B)),
          Fr(~m)
        ]
        --[ Secret(~m) ]->
        [ St_init_A($A, $B, ~m, sk(k_A), pk(k_A), pk(k_B)),
          St_init_B($A, $B, sk(k_B), pk(k_A), pk(k_B))
        ]

// ROLE A
rule asw1_A:
        [ St_init_A(A, B, m, sk(k_A), pk(k_A), pk(k_B)),
          Fr(~n_1)
        ]
        --[  ]->
        [ Out(aenc{<pk(k_A), pk(k_B), m, h(~n_1)>}sk(k_A)),
          St_asw1_A(A, B, m, ~n_1, sk(k_A), pk(k_A), pk(k_B))
        ]

rule asw2_A:
    let
        beta = aenc{<aenc{<pk(k_A), pk(k_B), m, h(n_1)>}sk(k_A), alpha>}sk(k_B)
    in
        [ St_asw1_A(A, B, m, n_1, sk(k_A), pk(k_A), pk(k_B)),
          In(beta)
        ]
        --[  ]->
        [ St_asw2_A(A, B, m, n_1, sk(k_A), pk(k_A), pk(k_B), beta, alpha)
        ]

rule asw3_A:
        [ St_asw2_A(A, B, m, n_1, sk(k_A), pk(k_A), pk(k_B), beta, alpha)
        ]
        --[  ]->
        [ Out(n_1),
          St_asw3_A(A, B, m, n_1, sk(k_A), pk(k_A), pk(k_B), beta, alpha)
        ]

rule asw4_A:
    let
        beta = aenc{<aenc{<pk(k_A), pk(k_B), m, h(n_1)>}sk(k_A), h(n_2)>}sk(k_B)
        alpha = h(n_2)
    in
        [ St_asw3_A(A, B, m, n_1, sk(k_A), pk(k_A), pk(k_B), beta, alpha),
          In(n_2)
        ]
        --[  ]->
        [ St_asw4_A(A, B, m, n_1, n_2, sk(k_A), pk(k_A), pk(k_B), beta)
        ]

// ROLE B
rule asw1_B:
    let
        beta = aenc{<pk(k_A), pk(k_B), m, alpha>}sk(k_A)
    in
        [ St_init_B(A, B, sk(k_B), pk(k_A), pk(k_B)),
          In(beta)
        ]
        --[  ]->
        [ St_asw1_B(A, B, m, sk(k_B), pk(k_A), pk(k_B), beta, alpha)
        ]

rule asw2_B:
        [ St_asw1_B(A, B, m, sk(k_B), pk(k_A), pk(k_B), beta, alpha),
          Fr(~n_2)
        ]
        --[  ]->
        [ Out(aenc{<beta, h(~n_2)>}sk(k_B)),
          St_asw2_B(A, B, m, ~n_2, sk(k_B), pk(k_A), pk(k_B), beta, alpha)
        ]

rule asw3_B:
    let
        beta = aenc{<pk(k_A), pk(k_B), m, h(n_1)>}sk(k_A)
        alpha = h(n_1)
    in
        [ St_asw2_B(A, B, m, n_2, sk(k_B), pk(k_A), pk(k_B), beta, alpha),
          In(n_1)
        ]
        --[  ]->
        [ St_asw3_B(A, B, m, n_1, n_2, sk(k_B), pk(k_A), pk(k_B), beta)
        ]

rule asw4_B:
        [ St_asw3_B(A, B, m, n_1, n_2, sk(k_B), pk(k_A), pk(k_B), beta)
        ]
        --[  ]->
        [ Out(n_2),
          St_asw4_B(A, B, m, n_1, n_2, sk(k_B), pk(k_A), pk(k_B), beta)
        ]

lemma Secrecy :
  "not (Ex m #t1 #t2 . Secret(m)@#t1 & K(m)@#t2)"
end

**The Attack Trace Tamarin-generated**
Attack trace for Secrecy:

Asymmetric_key_setup : [ Fr( ~f.1 ) ] --[  ]-> [ !Sk( $B, sk(~f.1) ), !Pk( $B, pk(~f.1) ) ]
Asymmetric_key_setup : [ Fr( ~f ) ] --[  ]-> [ !Sk( $A, sk(~f) ), !Pk( $A, pk(~f) ) ]
Init_Knowledge : [ !Pk( $A, pk(~f) ), !Pk( $B, pk(~f.1) ), !Sk( $A, sk(~f) ), !Sk( $B, sk(~f.1) ), Fr( ~m ) ] --[ Secret( ~m ) ]-> [ St_init_A( $A, $B, ~m, sk(~f), pk(~f), pk(~f.1) ), St_init_B( $A, $B, sk(~f.1), pk(~f), pk(~f.1) ) ]
asw1_A : [ St_init_A( $A, $B, ~m, sk(~f), pk(~f), pk(~f.1) ), Fr( ~n_1 ) ] --[  ]-> [ Out( aenc(<pk(~f), pk(~f.1), ~m, h(~n_1)>, sk(~f)) ), St_asw1_A( $A, $B, ~m, ~n_1, sk(~f), pk(~f), pk(~f.1) ) ]
AttRecv : aenc(<pk(~f), pk(~f.1), ~m, h(~n_1)>, sk(~f))
AttSend : K( ~m )

**The expected AnB attack trace output**
Types:
	A : A;
	B : B;
	E : Attacker;
Actions:
	A -> E : aenc{pkA, pkB, m, h(n.1)}skA;

"""


Example2_TranslateTrace=r"""
### Example 2
**The AnB protocol**
Protocol OTWAY_REES: 

Knowledge: 
    A: k(A, S), B; 
    B: k(B, S); 
    S: k(A, S), k(B, S); 
    
Actions: 
    [or1] A -> B (n1, i) : 
        i . A . B . senc{n1 . i . A . B}k(A, S); 
    [or2] B -> S (n2) : 
        i . A . B . senc{n1 . i . A . B}k(A, S) . senc{n2 . i . A . B}k(B, S); 
    [or3] S -> B (key) : 
        i . senc{n1 . key}k(A, S) . senc{n2 . key}k(B, S); 
    [or4] B -> A : 
        i . senc{n1 . key}k(A, S); 
  
end

**The Tamarin protocol**
theory OTWAY_REES
begin

functions: pk/1, sk/1, aenc/2, adec/2

builtins: symmetric-encryption

equations:
    adec(aenc(x.1, sk(x.2)), pk(x.2)) = x.1,
    adec(aenc(x.1, pk(x.2)), sk(x.2)) = x.1

rule Asymmetric_key_setup:
    [ Fr(~f) ] --> [ !Sk($A, sk(~f)), !Pk($A, pk(~f)) ]

rule Publish_public_keys:
    [ !Pk(A, pkA) ] --> [ Out(pkA) ]

rule Symmetric_key_setup:
    [ Fr(~symK) ] --> [ !Key($A, $B, ~symK) ]

rule Init_Knowledge:
        [ !Key($A, $S, k_A_S),
          !Key($B, $S, k_B_S),
          !Pk($A, pk(k_A)),
          !Pk($B, pk(k_B)),
          !Pk($S, pk(k_S)),
          !Sk($A, sk(k_A)),
          !Sk($B, sk(k_B)),
          !Sk($S, sk(k_S))
        ]
        --[  ]->
        [ St_init_A($A, $B, sk(k_A), pk(k_A), k_A_S),
          St_init_B($B, sk(k_B), pk(k_B), k_B_S),
          St_init_S($S, sk(k_S), pk(k_S), k_A_S, k_B_S)
        ]

// ROLE A
rule or1_A:
        [ St_init_A(A, B, sk(k_A), pk(k_A), k_A_S),
          Fr(~n1),
          Fr(~i)
        ]
        --[  ]->
        [ Out(<~i, A, B, senc{<~n1, ~i, A, B>}k_A_S>),
          St_or1_A(A, B, ~i, ~n1, sk(k_A), pk(k_A), k_A_S)
        ]

rule or4_A:
        [ St_or1_A(A, B, i, n1, sk(k_A), pk(k_A), k_A_S),
          In(<i, senc{<n1, key>}k_A_S>)
        ]
        --[ Commit_agreeA(key) ]->
        [ St_or4_A(A, B, i, key, n1, sk(k_A), pk(k_A), k_A_S)
        ]

// ROLE B
rule or1_B:
        [ St_init_B(B, sk(k_B), pk(k_B), k_B_S),
          In(<i, A, B, alpha>)
        ]
        --[  ]->
        [ St_or1_B(A, B, i, sk(k_B), pk(k_B), k_B_S, alpha)
        ]

rule or2_B:
        [ St_or1_B(A, B, i, sk(k_B), pk(k_B), k_B_S, alpha),
          Fr(~n2)
        ]
        --[  ]->
        [ Out(<i, A, B, alpha, senc{<~n2, i, A, B>}k_B_S>),
          St_or2_B(A, B, i, ~n2, sk(k_B), pk(k_B), k_B_S, alpha)
        ]

rule or3_B:
        [ St_or2_B(A, B, i, n2, sk(k_B), pk(k_B), k_B_S, alpha),
          In(<i, beta, senc{<n2, key>}k_B_S>)
        ]
        --[ Running_agreeA(key) ]->
        [ St_or3_B(A, B, i, key, n2, sk(k_B), pk(k_B), k_B_S, beta, alpha)
        ]

rule or4_B:
        [ St_or3_B(A, B, i, key, n2, sk(k_B), pk(k_B), k_B_S, beta, alpha)
        ]
        --[  ]->
        [ Out(<i, beta>),
          St_or4_B(A, B, i, key, n2, sk(k_B), pk(k_B), k_B_S, beta, alpha)
        ]

// ROLE S
rule or2_S:
        [ St_init_S(S, sk(k_S), pk(k_S), k_A_S, k_B_S),
          In(<i, A, B, senc{<n1, i, A, B>}k_A_S, senc{<n2, i, A, B>}k_B_S>)
        ]
        --[  ]->
        [ St_or2_S(A, B, S, i, n1, n2, sk(k_S), pk(k_S), k_A_S, k_B_S)
        ]

rule or3_S:
        [ St_or2_S(A, B, S, i, n1, n2, sk(k_S), pk(k_S), k_A_S, k_B_S),
          Fr(~key)
        ]
        --[  ]->
        [ Out(<i, senc{<n1, ~key>}k_A_S, senc{<n2, ~key>}k_B_S>),
          St_or3_S(A, B, S, i, ~key, n1, n2, sk(k_S), pk(k_S), k_A_S, k_B_S)
        ]

lemma agreeA:
    " (All m1 #i .
        Commit_agreeA(m1)@ #i
        ==>
        (Ex #j . Running_agreeA(m1) @ #j & #j < #i) &
        (not (Ex #j . Commit_agreeA(m1) @ #j & not (#i = #j)))
    )"


end

**The Tamarin-generated attack trace**

Attack trace for agreeA:

Asymmetric_key_setup : [ Fr( ~f.2 ) ] --[  ]-> [ !Sk( $S, sk(~f.2) ), !Pk( $S, pk(~f.2) ) ]
Asymmetric_key_setup : [ Fr( ~f.1 ) ] --[  ]-> [ !Sk( $B, sk(~f.1) ), !Pk( $B, pk(~f.1) ) ]
Asymmetric_key_setup : [ Fr( ~f ) ] --[  ]-> [ !Sk( $A, sk(~f) ), !Pk( $A, pk(~f) ) ]
Symmetric_key_setup : [ Fr( ~symK ) ] --[  ]-> [ !Key( $A, $S, ~symK ) ]
Init_Knowledge : [ !Key( $A, $S, ~symK ), !Key( $B, $S, ~symK.1 ), !Pk( $A, pk(~f) ), !Pk( $B, pk(~f.1) ), !Pk( $S, pk(~f.2) ), !Sk( $A, sk(~f) ), !Sk( $B, sk(~f.1) ), !Sk( $S, sk(~f.2) ) ] --[  ]-> [ St_init_A( $A, $B, sk(~f), pk(~f), ~symK ), St_init_B( $B, sk(~f.1), pk(~f.1), ~symK.1 ), St_init_S( $S, sk(~f.2), pk(~f.2), ~symK, ~symK.1 ) ]
or1_A : [ St_init_A( $A, $B, sk(~f), pk(~f), ~symK ), Fr( ~n1 ), Fr( ~i.1 ) ] --[  ]-> [ Out( <~i.1, $A, $B, senc(<~n1, ~i.1, $A, $B>, ~symK)> ), St_or1_A( $A, $B, ~i.1, ~n1, sk(~f), pk(~f), ~symK ) ]
AttRecv : <~i.1, $A, $B, senc(<~n1, ~i.1, $A, $B>, ~symK)>
AttSend : K( <~i.1, senc(<~n1, ~i.1, $A, $B>, ~symK)> )
or4_A : [ St_or1_A( $A, $B, ~i.1, ~n1, sk(~f), pk(~f), ~symK ), In( <~i.1, senc(<~n1, ~i.1, $A, $B>, ~symK)> ) ] --[ Commit_agreeA( <~i.1, $A, $B> ) ]-> [ St_or4_A( $A, $B, ~i.1, <~i.1, $A, $B>, ~n1, sk(~f), pk(~f), ~symK) ]


**The Expected AnB attack trace output**
Types:
	A : A;
	B : B;
	E : Attacker;
Actions:
	A -> E : i.1 . A . B . senc{n1 . i.1 . A . B}k(A,B);
	E -> A : i.1 . senc{n1 . i.1 . A . B}k(A,B);

"""

Example3_TranslateTrace=r"""
### Example 3
**The AnB protocol**
Protocol DIFFIE_HELLMAN:
 
Declarations:
    g/0;

Knowledge: 
    A : sec1, sec2;
    B : sec1, sec2;
    
Actions: 
    [dh_1] A -> B (x) : sec1 . g()^x; 
    [dh_2] B -> A (y) : g()^y; 
    [dh_3] A -> B (key) : sec2 . senc{key}(g()^(x*y));
    [dh_4] B -> A (m) : senc{m}(key); 
    
end

**The Tamarin protocol**
theory DIFFIE_HELLMAN
begin

functions: pk/1, sk/1, aenc/2, adec/2, g/0

builtins: diffie-hellman, symmetric-encryption

equations:
    adec(aenc(x.1, sk(x.2)), pk(x.2)) = x.1,
    adec(aenc(x.1, pk(x.2)), sk(x.2)) = x.1

rule Asymmetric_key_setup:
    [ Fr(~f) ] --> [ !Sk($A, sk(~f)), !Pk($A, pk(~f)) ]

rule Publish_public_keys:
    [ !Pk(A, pkA) ] --> [ Out(pkA) ]

rule Symmetric_key_setup:
    [ Fr(~symK) ] --> [ !Key($A, $B, ~symK) ]

rule Init_Knowledge:
        [ !Pk($A, pk(k_A)),
          !Pk($B, pk(k_B)),
          !Sk($A, sk(k_A)),
          !Sk($B, sk(k_B)),
          Fr(~sec1),
          Fr(~sec2)
        ]
        --[  ]->
        [ St_init_A($A, ~sec1, ~sec2, sk(k_A), pk(k_A)),
          St_init_B($B, ~sec1, ~sec2, sk(k_B), pk(k_B))
        ]

// ROLE A
rule dh_1_A:
        [ St_init_A(A, sec1, sec2, sk(k_A), pk(k_A)),
          Fr(~x)
        ]
        --[  ]->
        [ Out(<sec1, (g() ^ ~x)>),
          St_dh_1_A(A, sec1, sec2, ~x, sk(k_A), pk(k_A))
        ]

rule dh_2_A:
        [ St_dh_1_A(A, sec1, sec2, x, sk(k_A), pk(k_A)),
          In(alpha)
        ]
        --[  ]->
        [ St_dh_2_A(A, sec1, sec2, x, sk(k_A), pk(k_A), alpha)
        ]

rule dh_3_A:
        [ St_dh_2_A(A, sec1, sec2, x, sk(k_A), pk(k_A), alpha),
          Fr(~key)
        ]
        --[  ]->
        [ Out(<sec2, senc{~key}(alpha ^ x)>),
          St_dh_3_A(A, ~key, sec1, sec2, x, sk(k_A), pk(k_A), alpha)
        ]

rule dh_4_A:
        [ St_dh_3_A(A, key, sec1, sec2, x, sk(k_A), pk(k_A), alpha),
          In(senc{m}key)
        ]
        --[  ]->
        [ St_dh_4_A(A, key, m, sec1, sec2, x, sk(k_A), pk(k_A), alpha)
        ]

// ROLE B
rule dh_1_B:
        [ St_init_B(B, sec1, sec2, sk(k_B), pk(k_B)),
          In(<sec1, alpha>)
        ]
        --[  ]->
        [ St_dh_1_B(B, sec1, sec2, sk(k_B), pk(k_B), alpha)
        ]

rule dh_2_B:
        [ St_dh_1_B(B, sec1, sec2, sk(k_B), pk(k_B), alpha),
          Fr(~y)
        ]
        --[  ]->
        [ Out((g() ^ ~y)),
          St_dh_2_B(B, sec1, sec2, ~y, sk(k_B), pk(k_B), alpha)
        ]

rule dh_3_B:
        [ St_dh_2_B(B, sec1, sec2, y, sk(k_B), pk(k_B), alpha),
          In(<sec2, senc{key}(alpha ^ y)>)
        ]
        --[  ]->
        [ St_dh_3_B(B, key, sec1, sec2, y, sk(k_B), pk(k_B), alpha)
        ]

rule dh_4_B:
        [ St_dh_3_B(B, key, sec1, sec2, y, sk(k_B), pk(k_B), alpha),
          Fr(~m)
        ]
        --[ Secret(~m) ]->
        [ Out(senc{~m}key),
          St_dh_4_B(B, key, ~m, sec1, sec2, y, sk(k_B), pk(k_B), alpha)
        ]

lemma Secrecy :
  "not (
    Ex m #t1 #t2 .
      Secret(m) @ #t1 &
      K(m) @ #t2
  )"

end


**The Tamarin-generated attack trace**

Attack trace for Secrecy:

AttSend : K( alpha )
Asymmetric_key_setup : [ Fr( ~f ) ] --[  ]-> [ !Sk( $B, sk(~f) ), !Pk( $B, pk(~f) ) ]
Asymmetric_key_setup : [ Fr( ~f.1 ) ] --[  ]-> [ !Sk( $A, sk(~f.1) ), !Pk( $A, pk(~f.1) ) ]
Init_Knowledge : [ !Pk( $A, pk(~f.1) ), !Pk( $B, pk(~f) ), !Sk( $A, sk(~f.1) ), !Sk( $B, sk(~f) ), Fr( ~sec1 ), Fr( ~sec2 ) ] --[  ]-> [ St_init_A( $A, ~sec1, ~sec2, sk(~f.1), pk(~f.1) ), St_init_B( $B, ~sec1, ~sec2, sk(~f), pk(~f) ) ]
dh_1_A : [ St_init_A( $A, ~sec1, ~sec2, sk(~f.1), pk(~f.1) ), Fr( ~x ) ] --[  ]-> [ Out( <~sec1, g^~x> ), St_dh_1_A( $A, ~sec1, ~sec2, ~x, sk(~f.1), pk(~f.1) ) ]
dh_2_A : [ St_dh_1_A( $A, ~sec1, ~sec2, ~x, sk(~f.1), pk(~f.1) ), In( alpha ) ] --[  ]-> [ St_dh_2_A( $A, ~sec1, ~sec2, ~x, sk(~f.1), pk(~f.1), alpha ) ]
dh_3_A : [ St_dh_2_A( $A, ~sec1, ~sec2, ~x, sk(~f.1), pk(~f.1), alpha ), Fr( ~key.1 ) ] --[  ]-> [ Out( <~sec2, senc(~key.1, alpha^~x)> ), St_dh_3_A( $A, ~key.1, ~sec1, ~sec2, ~x, sk(~f.1), pk(~f.1), alpha) ]
AttRecv : <~sec2, senc(~key.1, alpha^~x)>
AttRecv : <~sec1, g^~x>
AttSend : K( <~sec1, g> )
dh_1_B : [ St_init_B( $B, ~sec1, ~sec2, sk(~f), pk(~f) ), In( <~sec1, g> ) ] --[  ]-> [ St_dh_1_B( $B, ~sec1, ~sec2, sk(~f), pk(~f), g ) ]
dh_2_B : [ St_dh_1_B( $B, ~sec1, ~sec2, sk(~f), pk(~f), g ), Fr( ~y ) ] --[  ]-> [ Out( g^~y ), St_dh_2_B( $B, ~sec1, ~sec2, ~y, sk(~f), pk(~f), g ) ]
AttRecv : g^~y
AttSend : K( <~sec2, senc(key, g^~y)> )
dh_3_B : [ St_dh_2_B( $B, ~sec1, ~sec2, ~y, sk(~f), pk(~f), g ), In( <~sec2, senc(key, g^~y)> ) ] --[  ]-> [ St_dh_3_B( $B, key, ~sec1, ~sec2, ~y, sk(~f), pk(~f), g ) ]
dh_4_B : [ St_dh_3_B( $B, key, ~sec1, ~sec2, ~y, sk(~f), pk(~f), g ), Fr( ~m ) ] --[ Secret( ~m ) ]-> [ Out( senc(~m, key) ), St_dh_4_B( $B, key, ~m, ~sec1, ~sec2, ~y, sk(~f), pk(~f), g ) ]
AttRecv : senc(~m, key)
AttSend : K( ~m )


**The Expected AnB attack trace output**

Types :
	A : A;
	B : B;
	E : Attacker;
Actions:
	A -> E : sec1 . g()^x;
	E -> A : alpha;
	A -> E : sec2 . senc{key.1}(alpha^x);
	E -> B : sec1 . g();
	B -> E : g()^y;
	E -> B : sec2 . senc{key}(g()^y);
	B -> E : senc{m}key;
"""