<template>
    <div>
        <nav-bar></nav-bar>
        <br>
        <b-container fluid>
            <h4>Project : {{ projectActual }}</h4>
            <hr>
            <br>
            <b-card no-body>
                <b-tabs pills card>
                    <b-tab title="Feature/User Stories" active>
                        <template v-for="(item, index) in singleProjectQuery.userStoryByProject">
                            <b-card no-body class="mb-1">
                              <b-card-header header-tag="header" class="p-1" role="tab">
                                <b-button block href="#" v-b-toggle="'feature-'+index"
                                          style="text-align: left;background-color: #CCCCCC;color: #7957d5">Feature/User Stories - {{ item.shortName }}</b-button>
                              </b-card-header>
                              <b-collapse :id="'feature-'+index" visible accordion="my-accordion" role="tabpanel">
                                <b-card-body>
                                  <p class="card-text" style="margin-left: 4%;">{{ item.description }}</p>
                                     <template v-for="(single_item,sl) in item.abuses">
                                <b-card no-body class="mb-1">
                                  <b-card-header header-tag="header" class="p-1" role="tab" style="margin-left: 4%;">
                                    <b-button block href="#" v-b-toggle="'hello-'+sl+item.shortName"
                                              style="text-align: left;background-color: #CCCCCC;color: #7957d5">Abuser Stories - {{ single_item.shortName }}</b-button>
                                  </b-card-header>
                                  <b-collapse :id="'hello-'+sl+item.shortName" visible accordion="my-accordionss" role="tabpanel">
                                    <b-card-body>
                                      <p class="card-text" style="margin-left: 6%;">{{ single_item.description }}</p>
                                        <template v-for="(single_scene,count) in single_item.models">
                                <b-card no-body class="mb-1" style="margin-left: 6%;">
                                  <b-card-header header-tag="header" class="p-1" role="tab" >
                                    <b-button block href="#" v-b-toggle="'Threat-'+count+item.shortName+single_item.shortName"
                                              style="text-align: left;background-color: #CCCCCC;color: #7957d5">
                                        Threat Scenarios - {{ single_scene.name }} <span class="label-high" v-if="single_scene.severity === 3" style="float: right;">High</span>
                                      <span class="label-medium" v-if="single_scene.severity === 2" style="float: right;">Medium</span>
                                      <span class="label-low" v-if="single_scene.severity === 1 || single_scene.severity === 0" style="float: right;">Low</span>
                                    </b-button>
                                  </b-card-header>
                                  <b-collapse :id="'Threat-'+count+item.shortName+single_item.shortName" visible accordion="my-accordions" role="tabpanel">
                                    <b-card-body>
                                      <p class="card-text">{{ single_scene.description }}</p>
                                    </b-card-body>
                                  </b-collapse>
                                </b-card>
                                </template>
                                    </b-card-body>
                                  </b-collapse>
                                </b-card>
                            </template>
                                </b-card-body>
                              </b-collapse>
                            </b-card>
                        </template>
                    </b-tab>
                    <b-tab title="Vulnerabilities">
                        <template v-for="(target, index) in singleProjectQuery.tgtByProject">
                            <b-card no-body class="mb-1">
                                <b-card-header header-tag="header" class="p-1" role="tab">
                                <b-button block href="#" v-b-toggle="'target-'+index"
                                          style="text-align: left;background-color: #CCCCCC;color: #7957d5">Target - {{ target.name }}</b-button>
                              </b-card-header>
                                <b-collapse :id="'target-'+index" visible accordion="my-accordion" role="tabpanel">
                                    <template v-for="(scan,sl) in target.scans">
                                        <b-card no-body class="mb-1">
                                            <b-card-header header-tag="header" class="p-1" role="tab" style="margin-left: 4%;">
                                                <b-button block href="#" v-b-toggle="'scan-'+sl+target.name"
                                              style="text-align: left;background-color: #CCCCCC;color: #7957d5">Scan - {{ scan.name }}</b-button>
                                            </b-card-header>
                                  <b-collapse :id="'scan-'+sl+target.name" visible accordion="my-accordionss" role="tabpanel">
                                    <b-card-body>
                                        <template v-for="(vul,count) in scan.vulnerabilities">
                                            <b-card no-body class="mb-1">
                                                <b-card-header header-tag="header" class="p-1" role="tab" style="margin-left: 4%;">
                                                    <b-button block href="#" v-b-toggle="'vul-'+count+scan.name"
                                              style="text-align: left;background-color: #CCCCCC;color: #7957d5">Vulnerability - {{ vul.name }}
                                                        <span class="label-high" v-if="vul.severity === 3" style="float: right;">High</span>
                                                        <span class="label-medium" v-if="vul.severity === 2" style="float: right;">Medium</span>
                                                        <span class="label-low" v-if="vul.severity === 1 || vul.severity === 0" style="float: right;">Low</span>
                                                    </b-button>
                                                </b-card-header>
                                                <b-collapse :id="'vul-'+count+scan.name" visible accordion="my-accordions" role="tabpanels">
                                                    <b-row style="margin-left: 5%;margin-top: 5%;">
                                                        <b-col cols="2">
                                                            <p v-if="vul.name">Name : </p>
                                                            <p v-if="vul.tool">Tool : </p>

                                                        </b-col>
                                                        <b-col cols="4">
                                                            <p v-if="vul.name">{{ vul.name }}</p>
                                                            <p v-if="vul.tool">{{ vul.tool }}</p>
                                                        </b-col>
                                                        <b-col cols="2">
                                                            <p v-if="vul.cwe">cwe :</p>
                                                        </b-col>
                                                        <b-col cols="4">
                                                            <p v-if="vul.cwe">{{ vul.cwe }}</p>
                                                        </b-col>
                                                        <br>
                                                        <b-col>
                                                            <p><span>Description : </span>{{ vul.description }}</p>
                                                            <p><span>Remediation : </span>{{ vul.remediation }}</p>
                                                            <p><span>Observation : </span>{{ vul.observation }}</p>
                                                        </b-col>
                                                    </b-row>
                                                    <!--<template v-if="vul.evidences.length > 0">-->
                                                    <!--<template v-for="(evid,num) in vul.evidences">-->
                                                        <!--<b-button block href="#" v-b-toggle="'evi-'+num+vul.name+scan.name"-->
                                              <!--style="text-align: left;background-color: #CCCCCC;color: #7957d5;margin-left: 4%;">Evidences-->
                                                        <!--</b-button>-->
                                                        <!--{{ evid }}-->
                                                        <!--<b-collapse :id="'evi-'+num+vul.name+scan.name" visible accordion="my-accordionses" role="tabpanelses" style="margin-left: 12%;">-->
                                                           <!--<b-row style="margin-top: 5%">-->
                                                               <!--<b-col cols="2">-->
                                                                   <!--<p>Attack : </p>-->
                                                                   <!--<p>Evidence : </p>-->
                                                                   <!--<p>OtherInfo : </p>-->
                                                                   <!--<p>URL : </p>-->
                                                               <!--</b-col>-->
                                                               <!--<b-col cols="4">-->
                                                                   <!--<p>{{ evid.attack }}</p>-->
                                                                   <!--<p>{{ evid.evidence }}</p>-->
                                                                   <!--<p>{{ evid.otherInfo }}</p>-->
                                                                   <!--<p>{{ evid.url }}</p>-->
                                                               <!--</b-col>-->
                                                               <!--<b-col cols="2">-->
                                                                   <!--<p>Log : </p>-->
                                                                   <!--<p>Name : </p>-->
                                                                   <!--<p>Param : </p>-->
                                                               <!--</b-col>-->
                                                               <!--&lt;!&ndash;<b-col cols="4">&ndash;&gt;-->
                                                                   <!--<p>{{ evid.log | decode }}</p>-->
                                                                   <!--&lt;!&ndash;<p>{{ evid.name }}</p>&ndash;&gt;-->
                                                                   <!--&lt;!&ndash;<p>{{ evid.param }}</p>&ndash;&gt;-->
                                                               <!--&lt;!&ndash;</b-col>&ndash;&gt;-->
                                                           <!--</b-row>-->
                                                        <!--</b-collapse>-->
                                                    <!--</template>-->
                                                        <!--</template>-->
                                                </b-collapse>
                                            </b-card>
                                        </template>
                                    </b-card-body>
                                  </b-collapse>
                                        </b-card>
                                    </template>
                                </b-collapse>
                            </b-card>
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
          tgtByProject(project: $pname) {
            name
                scans{
                  name
                  vulnerabilities{
                    name
                    description
                    cwe
                    observation
                    remediation
                    severity
                    tool
                    evidences{
                      attack
                      evidence
                      log
                      name
                      otherInfo
                      param
                      url
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
                update: result => result
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
