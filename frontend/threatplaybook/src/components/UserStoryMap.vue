<template>
    <div>
        <Navbar></Navbar>
        <loading :active.sync="isLoading" :can-cancel="true" :is-full-page="isLoading"></loading>
        <h5 class="text-center">User Story Map of <b>{{ projectActual }}</b></h5>
        <b-row>

            <b-col cols="12">
                <div>
                    <network
                            class="network"
                            ref="network"
                            :nodes="network.nodes"
                            :edges="network.edges"
                            :options="network.options"
                            @select-node="setClickEvent()"
                    ></network>
                </div>
                <div v-if="nodeCaption" class="report">
                    <div class="tile">
                        <div class="tile is-parent is-vertical">
                            <article class="tile is-child notification is-primary">
                                <p style="word-wrap: break-word;overflow-wrap: break-word;hyphens: auto;text-align: center;">
                                    <strong>{{ nodeLabel }} : </strong>
                                    {{ nodeCaption }}</p>
                            </article>
                        </div>
                    </div>
                </div>
            </b-col>
        </b-row>
    </div>
</template>
<script>
    import Navbar from "./Navbar.vue";
    import gql from "graphql-tag";
    import {Network} from "vue2vis";
    import "vue2vis/dist/vue2vis.css";
    import Loading from 'vue-loading-overlay'
    import 'vue-loading-overlay/dist/vue-loading.css';
    import axios from '@/utils/auth'

    const uuidv1 = require('uuid/v1');

    export default {
        name: 'UserStoryMap',
        props: ["projectName"],
        components: {
            Navbar,
            Network,
            Loading
        },
        data() {
            return {
                projectActual: atob(this.projectName),
                isLoading: false,
                network: {
                    nodes: [],
                    edges: [],
                    options: {
                        autoResize: true,
                        width: '100%',
                        height: '100%',
                        nodes: {
                            shape: "box",
                            widthConstraint: {minimum: 150, maximum: 176,},
                            widthConstraint: {minimum: 150, maximum: 176,},
                            heightConstraint: {valign: 'middle'}
                        },
                        layout: {
                            improvedLayout: false,
                            hierarchical: {
                                direction: "LR",
                                sortMethod: "directed",
                            }
                        },
                        edges: {
                            smooth: {
                                forceDirection: "UD"
                            }
                        },
                        physics: {
                            enabled: true
                        },

                    }
                },
                nodeCaption: "",
                nodeLabel: ""
            };
        },
        created() {
            this.project_name = this.$route.params.projectName
            this.actual_project_name = atob(this.$route.params.projectName)
            this.fetchGraphData();
        },
        methods: {
            setClickEvent: function () {
                this.$refs.network.$on("click", e => {
                    this.getSelectedNodeObject(e.nodes.toString());
                });
            },
            getSelectedNodeObject: function (inNodeID) {
                for (let i = 0; i < Object.keys(this.network.nodes).length; i++) {
                    if (this.network.nodes[i].id == inNodeID) {
                        console.log("label", this.network.nodes[i].label)
                        console.log("title", this.network.nodes[i].title)
                        this.nodeLabel = this.network.nodes[i].label
                        this.nodeCaption = this.network.nodes[i].title;
                    }
                }
                return null;
            },
            fetchGraphData() {
                this.isLoading = true
                console.log("projectActual", this.projectActual)
                const projName = `"${this.projectActual}"`
                axios.post('/graph', {
                    query: '{\n' +
                        'userStoryByProject(project:' + projName + '){\n' +
                            'shortName\n'+
                            'description\n'+
                        'relations{ \n' +
                        'dataFlow\n' +
                        'endpoint\n' +
                        'nature\n' +
                        '}\n' +
                        '}\n' +
                        '}'
                })
                    .then(res => {
                        this.isLoading = false
                //Code to push data into the nodes
                this.network.nodes.push({
                    id: 1,
                    label: `Project: ${this.projectActual}`
                });
                for (let singleFeature of res.data.data.userStoryByProject) {
                    let featureRandom = uuidv1()
                    this.network.nodes.push({
                        id: featureRandom,
                        label: singleFeature.shortName,
                        title: singleFeature.description,
                        color: {
                            background: "#3399ff"
                        }
                    });
                    let edgeFeatureRandom = uuidv1()
                    this.network.edges.push({
                        id: edgeFeatureRandom,
                        from: 1,
                        to: featureRandom,
                        color: {
                            highlight: "#3399ff"
                        }
                    });
                    for (let singleAbuse of singleFeature.relations) {
                        let abuseRandom = uuidv1()
                        this.network.nodes.push({
                            id: abuseRandom,
                            label: singleAbuse.endpoint,
                            title: singleAbuse.dataFlow,
                            color: {
                                background: "#ffb99d"
                            }
                        });
                        let edgeAbuseRandom = uuidv1()
                        this.network.edges.push({
                            id: edgeAbuseRandom,
                            from: featureRandom,
                            to: abuseRandom,
                            color: {
                                highlight: "#ffb99d"
                            }
                        });
                    }
                }
                 })
                    .catch(error => {
                        this.isLoading = false
                    })
            }
        }

    };
</script>
<style>
    .network {
        height: 500px;
        border: 1px solid #ccc;
        margin: 2%;
    }

    .report {
        display: inline-block;
        margin-left: 5%;
        margin-right: 5%;
        text-align: center;
    }

</style>
