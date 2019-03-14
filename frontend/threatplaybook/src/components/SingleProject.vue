<template>
    <div>
        <loading :active.sync="isLoading" :can-cancel="true" :is-full-page="isLoading"></loading>
        <nav-bar></nav-bar>
        <br>
        <b-container fluid>
            <h4>Project : {{ projectActual }}</h4>
            <hr>
            <br>
            <b-card no-body>
                <b-tabs pills card>
                    <b-tab title="Feature/User Stories" active>
                        <div class="ibox" style="background-color: #1b2034; color:#FFFFFF;">
                            <br>
                            <div class="ibox-body">
                                <div class="streamline" style="padding-left: 20px;">
                                    <div class="sl-item sl-primary">
                                        <div class="sl-content">
                                            <template v-for="story in featureData">
                                                <h3 style="font-weight: 600; font-size: 24px;"> UserStory : {{
                                                    story.shortName }}</h3>
                                                <p><b>Description:</b> {{ story.description }}</p>
                                                <div class="streamline" style="padding-left: 20px;">
                                                    <div class="sl-item sl-primary">
                                                        <div class="sl-content">
                                                            <template v-for="abuse in story.abuses">
                                                                <h4 style="font-weight: 600; font-size: 20px;">Abuses :
                                                                    {{ abuse.shortName }}</h4>
                                                                <p><b>Description:</b> {{ abuse.description }}</p>
                                                                <div class="streamline" style="padding-left: 20px;">
                                                                    <div class="sl-item sl-primary">
                                                                        <div class="sl-content">
                                                                            <template v-for="vul in abuse.models">
                                                                                <h4 style="font-weight: 600; font-size: 20px;">
                                                                                    Vulnerability : {{ vul.name }}
                                                                                    <span class="label-high"
                                                                                          v-if="vul.severity === 3">High</span>
                                                                                    <span class="label-medium"
                                                                                          v-if="vul.severity === 2">Medium</span>
                                                                                    <span class="label-low"
                                                                                          v-if="vul.severity === 1">Low</span>
                                                                                </h4>
                                                                                <p><b>Description:</b> {{
                                                                                    vul.description }}</p>
                                                                                <div class="streamline"
                                                                                     style="padding-left: 20px;">
                                                                                    <div class="sl-item sl-primary">
                                                                                        <div class="sl-content">
                                                                                            <template
                                                                                                    v-for="test in vul.tests">
                                                                                                <p><b>TestCase Name
                                                                                                    : </b>{{ test.name
                                                                                                    }}</p>
                                                                                                <p><b>TestCase: </b>{{
                                                                                                    test.testCase }}</p>
                                                                                            </template>
                                                                                        </div>
                                                                                    </div>
                                                                                </div>
                                                                            </template>
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            </template>
                                                        </div>
                                                    </div>
                                                </div>
                                            </template>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </b-tab>
                    <b-tab title="Scans" @click="getAllScans">
                        <br>
                        <template v-for="scan in allScans">
                            <b-list-group>
                                <b-list-group-item>
                                    <a @click="individualScan(scan.name)" style="cursor: pointer;">
                                        {{ scan.name }}
                                    </a>
                                    <!--<span style="float: right;">-->
                                    <!--<b-badge variant="success" v-if="scan.synced">synced</b-badge>-->
                                    <!--<font-awesome-icon icon="sync" v-else/>-->
                                    <!--</span>-->
                                    <span style="float: right;">
                                        {{ scan.createdOn | timeFilter}}
                                    </span>
                                </b-list-group-item>
                            </b-list-group>
                            <br>
                        </template>
                    </b-tab>
                </b-tabs>
            </b-card>
        </b-container>
    </div>
</template>
<script>
    import Navbar from "./Navbar.vue";
    import gql from "graphql-tag";
    import Loading from 'vue-loading-overlay'
    import 'vue-loading-overlay/dist/vue-loading.css';
    import axios from '@/utils/auth'
    import moment from 'moment'


    export default {
        props: ["projectName"],
        components: {
            "nav-bar": Navbar,
            Loading
        },
        data() {
            return {
                isLoading: false,
                featureData: '',
                allScans: '',
            };
        },
        created() {
            this.projectActual = atob(this.$route.params.projectName)
            this.projectName = this.$route.params.projectName
            this.fetchData()
        },
        methods: {
            goToProjectMap() {
                this.$router.push("/map/" + this.projectName);
            },

            fetchData() {
                if (this.projectActual) {
                    this.isLoading = true
                    const project = `"${this.projectActual}"`
                    axios.post('/graph', {
                        query: '{\n' +
                            'userStoryByProject(project:' + project + '){\n' +
                            'shortName \n' +
                            'description \n' +
                            'abuses{ \n' +
                            'shortName \n' +
                            'description \n' +
                            'models{ \n' +
                            'name \n' +
                            'severity \n' +
                            'description \n' +
                            'tests{ \n' +
                            'name \n' +
                            'testCase \n' +
                            '} \n' +
                            '} \n' +
                            '} \n' +
                            '}\n' +
                            '}'
                    })
                        .then(res => {
                            this.isLoading = false
                            this.featureData = res.data.data.userStoryByProject
                        })
                        .catch(error => {
                            this.isLoading = false
                        })

                }
            },

            getAllScans() {
                this.isLoading = true
                axios.post('/graph', {
                    query: '{\n' +
                        'scans{\n' +
                        'name\n' +
                        'createdOn\n' +
                        'synced \n' +
                        '}\n' +
                        '}'
                })
                    .then(res => {
                        this.isLoading = false
                        this.allScans = res.data.data.scans
                    })
                    .catch(error => {
                        this.isLoading = false
                        console.log("Error", error)
                    })
            },

            individualScan(scanName) {
                const scan_name = btoa(scanName)
                this.$router.push("/scan/" + scan_name);
            }

        },
        filters: {
            timeFilter: function (value) {
                if (!value) return ''
                value = moment(String(value)).format('DD-MMM-YYYY hh:mm')
                return value
            }
        }
    };
</script>

<style>
    .label-high {
        width: 60px;
        border-radius: 0;
        text-shadow: none;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 5px 3px;
        text-align: center;
        color: #FFFFFF;
        background-color: #d11d55 !important
    }

    .label-medium {
        width: 60px;
        border-radius: 0;
        text-shadow: none;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 5px 3px;
        text-align: center;
        color: #FFFFFF;
        background-color: #ff9c2c !important
    }

    .label-low {
        width: 60px;
        border-radius: 0;
        text-shadow: none;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 5px 3px;
        text-align: center;
        color: #FFFFFF;
        background-color: #008b8f !important
    }


    .streamline .sl-primary {
        border-left-color: #188ae2;
    }

    .streamline .sl-item {
        position: relative;
        padding-bottom: 12px;
        border-left: 1px solid #ccc;
    }

    .streamline .sl-item .text-muted {
        color: inherit;
        opacity: .6;
    }

    .streamline .sl-item p {
        margin-bottom: 10px;
    }

    .streamline .sl-primary {
        border-left-color: #ff4a43;
    }

    .streamline .sl-danger {
        border-left-color: #22beef;
    }

    .streamline .sl-success {
        border-left-color: #a2d200;
    }

    .streamline .sl-warning {
        border-left-color: #8e44ad;
    }

    .streamline .sl-item:before {
        content: '';
        position: absolute;
        left: -6px;
        top: 0;
        background-color: #ccc;
        width: 12px;
        height: 12px;
        border-radius: 100%;
    }

    .streamline .sl-primary:before, .streamline .sl-primary:last-child:after {
        background-color: #ff4a43;
    }

    .streamline .sl-danger:before, .streamline .sl-danger:last-child:after {
        background-color: #22beef;
    }

    .streamline .sl-success:before, .streamline .sl-success:last-child:after {
        background-color: #a2d200;
    }

    .streamline .sl-warning:before, .streamline .sl-warning:last-child:after {
        background-color: #8e44ad;
    }

    .card .card-body.card-padding {
    / padding: 23 px 27 px;
    }

    .streamline .sl-item .sl-content {
        margin-left: 24px;
    }

    .panel-body .list-group {
        margin-bottom: 0;
    }
</style>
