<template>
    <div>
        <nav-bar></nav-bar>
        <br>
        <div class="column is-narrow"></div>
         <div class="column">
             <button class="button is-primary" slot="trigger" style="float: right" @click="goToProjectMap">Threat Map</button>
        <h2 class="title">Project: {{ projectActual }}</h2>
             <br>
        <b-tabs v-model="activeTab">

            <b-tab-item label="Feature/User Stories">
                <template v-for="item in singleProjectQuery">
                    <b-collapse class="panel" :open.sync="isOpen">
                        <div slot="trigger" class="panel-heading">
                            <strong>{{ item.shortName }}</strong>
                        </div>
                        <div class="panel-block">
                            {{ item.description }}
                        </div>
                    </b-collapse>
                </template>
            </b-tab-item>

            <b-tab-item label="Abuser Stories">
                <template v-for="item in singleProjectQuery">
                <template v-for="single_item in item.abuses">
                    <b-collapse class="panel" :open.sync="isOpen">
                        <div slot="trigger" class="panel-heading">
                            <strong>{{ single_item.shortName }}</strong>
                        </div>
                        <div class="panel-block">
                            {{ single_item.description }}
                        </div>
                    </b-collapse>
                </template>
                </template>
            </b-tab-item>

            <b-tab-item label="Threat Scenarios">
                <template v-for="item in singleProjectQuery">
                <template v-for="single_item in item.abuses">
                <template v-for="single_scene in single_item.models">
                    <b-collapse class="panel" :open.sync="isOpen">
                        <div slot="trigger" class="panel-heading">
                            <strong>{{ single_scene.name }}</strong>
                            <span class="label-high" v-if="single_scene.severity === 3" style="float: right;">High</span>
                            <span class="label-medium" v-if="single_scene.severity === 2" style="float: right;">Medium</span>
                            <span class="label-low" v-if="single_scene.severity === 1" style="float: right;">Low</span>
                            <span style="float: right;font-size: 14px;color: #000000;margin-right: 3%;">CWE: {{ single_scene.cwe }}</span>
                        </div>
                        <div class="panel-block">
                            <p>{{ single_scene.description }}</p>
                        </div>
                    </b-collapse>
                </template>
                </template>
                </template>
            </b-tab-item>

        </b-tabs>

         </div>
    </div>
</template>
<script>
    import Navbar from "./Navbar.vue";
    import gql from "graphql-tag";

    export default {
        props: ["projectName"],
        components: {
            "nav-bar": Navbar
        },
        data() {
            return {
                projectActual: atob(this.projectName),
                isOpen: false
            };
        },
        methods:{
            goToProjectMap() {
      this.$router.push("/map/" + this.projectName);
    }
        },
        apollo: {
            singleProjectQuery: {
                query: gql`
        query singleProjectQuery($pname: String!) {
          userStoryByProject(project: $pname) {
            shortName
            description
            abuses {
              shortName
              description
              models {
                name
                description
                cwe
                severity
                tests {
                  name
                  testCase
                  testType
                }
              }
            }
          }
        }
      `,
                variables() {
                    return {
                        pname: atob(this.projectName)
                    };
                },
                update: result => result.userStoryByProject
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
        background-color: #d11d55!important
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
        background-color: #ff9c2c!important
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
        background-color: #008b8f!important
    }
</style>
