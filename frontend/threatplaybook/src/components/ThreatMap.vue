<template>
    <div>
        <Navbar></Navbar>
        <loading :active.sync="isLoading" :can-cancel="true" :is-full-page="isLoading"></loading>
        <h5 class="text-center">Threat Map of <b>{{ projectActual }}</b></h5>
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
    import {Network} from "vue2vis";
    import "vue2vis/dist/vue2vis.css";
    import Loading from 'vue-loading-overlay'
    import 'vue-loading-overlay/dist/vue-loading.css';
    import axios from '../utils/auth'

    const uuidv1 = require('uuid/v1');

    export default {
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
                            // size: 15,
                            widthConstraint: {minimum: 150, maximum: 176,},
                            widthConstraint: {minimum: 150, maximum: 176,},
                            heightConstraint: {valign: 'middle'}
                        },
                        layout: {
                            improvedLayout: true,
                            hierarchical: {
                                direction: "UD",
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
        created(){
            this.project_name = this.$route.params.projectName
            this.actual_project_name = atob(this.$route.params.projectName)
            this.fetchGraphData()
        },

        methods: {
            setClickEvent: function () {
                this.$refs.network.$on("click", e => {
                    this.getSelectedNodeObject(e.nodes.toString())
                });
            },
            getSelectedNodeObject: function (inNodeID) {
                for (let i = 0; i < Object.keys(this.network.nodes).length; i++) {
                    if (this.network.nodes[i].id == inNodeID) {
                        this.nodeLabel = this.network.nodes[i].label
                        this.nodeCaption = this.network.nodes[i].title;
                    }
                }
                return null;
            },
            async fetchGraphData() {
                this.isLoading = true
                const projName = `"${this.projectActual}"`
                axios.post('/graph', {
                    query: '{\n' +
                        'userStoryByProject(project:' + projName + '){\n' +
                            'shortName\n'+
                            'description\n'+
                        'abuses{ \n' +
                        'shortName\n' +
                        'description\n' +
                        'models{ \n' +
                            'name\n'+
                            'description\n'+
                            'cwe\n'+
                            'severity\n'+
                        'tests{ \n' +
                            'name\n'+
                            'testCase\n'+
                            'testType\n'+
                        '}\n' +
                        '}\n' +
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
                        if (res.data.data.userStoryByProject.length > 0){
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
                    for (let singleAbuse of singleFeature.abuses) {
                        let abuseRandom = uuidv1()
                        this.network.nodes.push({
                            id: abuseRandom,
                            label: singleAbuse.shortName,
                            title: singleAbuse.description,
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

                        for (let singleScenario of singleAbuse.models) {
                            let sceneRandom = uuidv1()
                            this.network.nodes.push({
                                id: sceneRandom,
                                label: singleScenario.name,
                                title: singleScenario.description,
                                color: {
                                    background: "#FF6122"
                                }
                            });
                            let sceneEdgeRandom = uuidv1()
                            this.network.edges.push({
                                id: sceneEdgeRandom,
                                from: abuseRandom,
                                to: sceneRandom,
                                color: {
                                    highlight: "#FF6122"
                                }
                            });

                            for (let singleTest of singleScenario.tests) {
                                let testRandom = uuidv1()
                                this.network.nodes.push({
                                    id: testRandom,
                                    label: singleTest.name,
                                    title: singleTest.testCase,
                                    color: {
                                        background: "#16fd1a"
                                    }

                                });
                                let testEdgeRandom = uuidv1()
                                this.network.edges.push({
                                    id: testEdgeRandom,
                                    from: sceneRandom,
                                    to: testRandom,
                                    color: {
                                        highlight: "#16fd1a"
                                    }
                                });
                            }
                        }
                    }
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
