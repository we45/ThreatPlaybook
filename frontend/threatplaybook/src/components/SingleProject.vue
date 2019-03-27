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
                        <div class="row">
                            <div class="col-md-4">
                                <div class="card">
                                    <div class="card-body">
                                        <b-tree-view
                                                :data="featureData"
                                                :showIcons="true"
                                                iconClassProp="icon"
                                                prependIconClass="fas"
                                                :contextMenu="true"
                                                :contextMenuItems="contextMenuItems"
                                                @nodeSelect="nodeSelect"
                                        ></b-tree-view>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-8" v-if="selectedNode">
                                <template v-if="selectedUserStory.length > 0">
                                    <template v-for="userStory in selectedUserStory">
                                        <b-card :title="userStory.title">
                                            <hr>
                                            <p><b>Description : </b> {{ userStory.desc }}</p>
                                        </b-card>
                                    </template>
                                </template>

                                <template v-if="selectedAbuserStory.length > 0">
                                    <template v-for="abuserStory in selectedAbuserStory">
                                        <b-card :title="abuserStory.title">
                                            <hr>
                                            <p><b>Description : </b> {{ abuserStory.desc }}</p>
                                        </b-card>
                                    </template>
                                </template>

                                <template v-if="selectedVulDetail.length > 0">
                                    <template v-for="vul in selectedVulDetail">
                                        <b-card :title="vul.title">
                                            <hr>
                                            <b-row>
                                                <b-col cols="6">
                                                    <p class="text-left">
                                                        <b>CWE : </b>
                                                        {{ vul.cwe }}
                                                    </p>
                                                </b-col>
                                                <b-col cols="6">
                                                    <p class="text-left">
                                                        <b>Severity : </b>
                                                        <span class="label-high" v-if="vul.severity === 4">High</span>
                                                        <span class="label-high" v-if="vul.severity === 3">High</span>
                                                        <span class="label-medium" v-if="vul.severity === 2"
                                                        >Medium</span>
                                                        <span class="label-low" v-if="vul.severity === 1"
                                                        >Low</span>
                                                    </p>
                                                </b-col>
                                            </b-row>
                                            <p v-if="vul.desc"><b>Description : </b> {{ vul.desc }}</p>
                                            <template v-if="vul.mitigations">
                                                <p><b>Mitigations : </b></p>
                                                <hr>
                                                <p><b>Phase : </b>
                                                    <b-badge variant="info">{{ vul.mitigations.phase }}</b-badge>
                                                </p>
                                                <p><b>Strategy : </b>
                                                    <b-badge variant="success" pill>{{ vul.mitigations.strategy }}
                                                    </b-badge>
                                                </p>
                                                <p><b>Description : </b>{{ vul.mitigations.description}}</p>
                                            </template>
                                        </b-card>
                                    </template>
                                </template>

                                <template v-if="selectedTestCases.length > 0">
                                    <template v-for="testCase in selectedTestCases">
                                        <b-card :title="testCase.title">
                                            <hr>
                                            <p><b>Test Case : </b>{{ testCase.testCase }}</p>
                                            <p><b>Test Type : </b>{{ testCase.testType }}</p>
                                        </b-card>
                                    </template>
                                </template>
                            </div>
                        </div>
                    </b-tab>
                    <b-tab title="Scans" @click="getAllScans">
                        <br>
                        <template v-for="tgt in allScans">
                            <template v-for="scan in tgt.scans">
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
                                        <span style="float: right;margin-right: 2%;">{{ tgt.name }}</span>
                                    </b-list-group-item>
                                </b-list-group>
                                <br>
                            </template>
                        </template>
                    </b-tab>
                </b-tabs>
            </b-card>
        </b-container>
    </div>
</template>
<script>
    import Navbar from "./Navbar.vue"
    import Loading from "vue-loading-overlay"
    import "vue-loading-overlay/dist/vue-loading.css"
    import axios from "../utils/auth"
    import moment from "moment"
    import BCardText from "bootstrap-vue/src/components/card/card-text"

    export default {
        props: ["projectName"],
        components: {
            BCardText,
            "nav-bar": Navbar,
            Loading
        },
        data() {
            return {
                isLoading: false,
                featureData: [],
                allScans: "",
                contextMenuItems: [
                    {code: "DELETE_NODE", label: "Delete node"},
                    {
                        code: "ADD_CHILD_NODE",
                        label: "Add child"
                    },
                    {code: "RENAME_NODE", label: "Rename"}
                ],
                selectedNode: "",
                nodeSelectObject: {},
                selectedUserStory: [],
                selectedAbuserStory: [],
                selectedVulDetail: [],
                selectedTestCases: []
            }
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
                    this.isLoading = true;
                    const project = `"${this.projectActual}"`;
                    axios
                        .post("/graph", {
                            query:
                                "{\n" +
                                "userStoryByProject(project:" +
                                project +
                                "){\n" +
                                "id \n" +
                                "shortName \n" +
                                "description \n" +
                                "abuses{ \n" +
                                "id \n" +
                                "shortName \n" +
                                "description \n" +
                                "models{ \n" +
                                "id \n" +
                                "name \n" +
                                "severity \n" +
                                "description \n" +
                                "mitigations \n" +
                                "cwe \n" +
                                "tests{ \n" +
                                "id \n" +
                                "name \n" +
                                "testCase \n" +
                                "testType \n" +
                                "} \n" +
                                "} \n" +
                                "} \n" +
                                "}\n" +
                                "}"
                        })
                        .then(res => {
                            this.isLoading = false;
                            let responseData = res.data.data.userStoryByProject;
                            for (var single in responseData) {
                                var singleData = {
                                    id: "us:" + responseData[single].id,
                                    name: responseData[single].shortName,
                                    desc: responseData[single].description,
                                    icon: "fa-cubes",
                                    type: 'us',
                                    title: 'User Story'
                                };
                                if (responseData[single].abuses.length > 0) {
                                    singleData.children = [];
                                    for (var abuserStory in responseData[single].abuses) {
                                        var singleAbuse = {
                                            id: "as:" + responseData[single].abuses[abuserStory].id,
                                            name: responseData[single].abuses[abuserStory].shortName,
                                            desc: responseData[single].abuses[abuserStory].description,
                                            icon: "fa-warning",
                                            type: "as",
                                            title: "Abuser Story"
                                        };
                                        if (
                                            responseData[single].abuses[abuserStory].models.length > 0
                                        ) {
                                            singleAbuse.children = [];
                                            for (var singleModel in responseData[single].abuses[
                                                abuserStory
                                                ].models) {
                                                var sModel = {
                                                    id:
                                                        "mod:" +
                                                        responseData[single].abuses[abuserStory].models[
                                                            singleModel
                                                            ].id,
                                                    name:
                                                    responseData[single].abuses[abuserStory].models[
                                                        singleModel
                                                        ].name,
                                                    desc:
                                                    responseData[single].abuses[abuserStory].models[
                                                        singleModel
                                                        ].description,
                                                    severity:
                                                    responseData[single].abuses[abuserStory].models[
                                                        singleModel
                                                        ].severity,
                                                    mitigations: responseData[single].abuses[abuserStory].models[
                                                        singleModel
                                                        ].mitigations[0],
                                                    cwe:
                                                    responseData[single].abuses[abuserStory].models[
                                                        singleModel
                                                        ].cwe,
                                                    icon: "fa-bug",
                                                    type: "mod",
                                                    title: "Vulnerability"
                                                };
                                                if (
                                                    responseData[single].abuses[abuserStory].models[
                                                        singleModel
                                                        ].tests.length > 0
                                                ) {
                                                    sModel.children = [];
                                                    var allTests =
                                                        responseData[single].abuses[abuserStory].models[
                                                            singleModel
                                                            ].tests;
                                                    for (var singleTest in allTests) {
                                                        var sTest = {
                                                            id: "test" + allTests[singleTest].id,
                                                            name: allTests[singleTest].name,
                                                            icon: "fa fa-check-circle",
                                                            type: "tm",
                                                            title: "Threat Model",
                                                            testCase: allTests[singleTest].testCase,
                                                            testType: allTests[singleTest].testType,
                                                        };
                                                        sModel.children.push(sTest);
                                                    }
                                                }
                                                singleAbuse.children.push(sModel);
                                            }
                                        }
                                        singleData.children.push(singleAbuse);
                                    }
                                }
                                this.featureData.push(singleData);
                            }
                        })
                        .catch(error => {
                            this.isLoading = false;
                        });
                }
            },

            getAllScans() {
                this.isLoading = true;
                const project = `"${this.projectActual}"`;
                axios
                    .post("/graph", {
                        query:
                            "{\n" +
                            "tgtByProject(project:" +
                            project +
                            "){\n" +
                            "name \n" +
                            "scans{\n" +
                            "name\n" +
                            "createdOn\n" +
                            "synced \n" +
                            "}\n" +
                            "}" +
                            "}"
                    })
                    .then(res => {
                        this.isLoading = false
                        this.allScans = res.data.data.tgtByProject
                    })
                    .catch(error => {
                        this.isLoading = false
                    });
            },

            individualScan(scanName) {
                const scan_name = btoa(scanName);
                this.$router.push("/scan/" + scan_name);
            },

            nodeSelect(node, isSelected) {
                if (isSelected) {
                    this.selectedUserStory = []
                    this.selectedAbuserStory = []
                    this.selectedVulDetail = []
                    this.selectedTestCases = []
                    this.selectedNode = node.data;

                    if (this.selectedNode.type === 'us') {
                        this.selectedUserStory.push({
                            title: this.selectedNode.title,
                            desc: this.selectedNode.desc
                        })
                    }

                    if (this.selectedNode.type === 'as') {
                        this.selectedAbuserStory.push({
                            title: this.selectedNode.title,
                            desc: this.selectedNode.desc
                        })
                    }

                    if (this.selectedNode.type === 'mod') {
                        const mitigation = JSON.parse(this.selectedNode.mitigations)
                        this.selectedVulDetail.push({
                            title: this.selectedNode.title,
                            desc: this.selectedNode.desc,
                            cwe: this.selectedNode.cwe,
                            severity: this.selectedNode.severity,
                            mitigations: mitigation,
                        })
                    }

                    if (this.selectedNode.type === 'tm') {
                        this.selectedTestCases.push({
                            title: this.selectedNode.title,
                            testCase: this.selectedNode.testCase,
                            testType: this.selectedNode.testType,
                        })
                    }

                }
            }
        },
        filters: {
            timeFilter: function (value) {
                if (!value) return "";
                value = moment(String(value)).format("DD-MMM-YYYY hh:mm");
                return value;
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
        color: #ffffff;
        background-color: #d11d55 !important;
    }

    .label-medium {
        width: 60px;
        border-radius: 0;
        text-shadow: none;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 5px 3px;
        text-align: center;
        color: #ffffff;
        background-color: #ff9c2c !important;
    }

    .label-low {
        width: 60px;
        border-radius: 0;
        text-shadow: none;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 5px 3px;
        text-align: center;
        color: #ffffff;
        background-color: #008b8f !important;
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
        opacity: 0.6;
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
        content: "";
        position: absolute;
        left: -6px;
        top: 0;
        background-color: #ccc;
        width: 12px;
        height: 12px;
        border-radius: 100%;
    }

    .streamline .sl-primary:before,
    .streamline .sl-primary:last-child:after {
        background-color: #ff4a43;
    }

    .streamline .sl-danger:before,
    .streamline .sl-danger:last-child:after {
        background-color: #22beef;
    }

    .streamline .sl-success:before,
    .streamline .sl-success:last-child:after {
        background-color: #a2d200;
    }

    .streamline .sl-warning:before,
    .streamline .sl-warning:last-child:after {
        background-color: #8e44ad;
    }

    .card .card-body.card-padding {
        padding: 23px 27px;
    }

    .streamline .sl-item .sl-content {
        margin-left: 24px;
    }

    .panel-body .list-group {
        margin-bottom: 0;
    }
</style>
