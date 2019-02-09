<template>
    <div class="container">
        <div class="card">
            <header class="card-header">
                    <img alt="ThreatPlaybook Logo" src="../assets/tp-logo.png">
            </header>
            <div class="card-content">
                <b-field label="Email">
                    <b-input type="email"
                             value="john@"
                             maxlength="30">
                    </b-input>
                </b-field>
                <b-field label="Password">
                    <b-input value="123" type="password" maxlength="30"></b-input>
                </b-field>
                <button class="button is-primary">Login</button>
            </div>
        </div>
    </div>
</template>