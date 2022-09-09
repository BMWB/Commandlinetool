#!/usr/bin/ruby -w
# -*- coding: UTF-8 -*-

$VERBOSE = nil #close warnings
require 'xcodeproj'


class ProjManager
    def initialize(projectPath)
        @projectPath = projectPath
        @projectObj = Xcodeproj::Project.open(@projectPath)
        @mainDirName = File::basename(projectPath, '.xcodeproj')
    end

    def handleFiles(filePaths)
        validFiles = []
        token = "#{@mainDirName}/"
        for fp in filePaths
            if fp.start_with?(token)
                if (fp.index('.m') or fp.index('.mm')) and !fp.index('Pods/') and !fp.index('KZStaticAnalyzer/')
                    fileName = File::basename(fp)
                    validFiles << fileName
                end
            end
        end
        #search file refers
        fildRefs = __serachValidFileReferObjs(validFiles)

        #search target
        return __modifyTargets(fildRefs)
        
    end

    def saveModify
        @projectObj.save
    end

    def __serachValidFileReferObjs(validFiles)
        if validFiles.empty?
            return []
        end
        fildRefs = []
        for gr in @projectObj.main_group.recursive_children_groups
            if validFiles.empty?
                break
            end
            for fr in gr.files
                curFP = fr.path
                if curFP
                    curFn = File::basename(curFP)
                    if validFiles.include?(curFn)
                        fildRefs << fr
                        validFiles.delete(curFn)
                    end
                end
            end 
        end
        return fildRefs
    end

    def __modifyTargets(fildRefs)
        if fildRefs.empty?
            return ''
        end
        tipString = ''
        targets = @projectObj.targets
        for tar in targets
            if !tar.instance_of?(Xcodeproj::Project::Object::PBXNativeTarget) or !tar.launchable_target_type?
                next
            end 
            needInserts = []
            sourcePhase = tar.source_build_phase
            for findRf in fildRefs
                if !(sourcePhase.include?(findRf))
                    tipString.concat("#{tar.name} target added reference of #{File::basename(findRf.path)}\n")
                    needInserts << findRf
                end
            end
            if  !(needInserts.empty?)
                tar.add_file_references(needInserts)
            end
        end
        return tipString
    end

    private :__serachValidFileReferObjs, :__modifyTargets

end



if  !ARGV.empty? and ARGV.length > 1
    projPath = ARGV[0]
    if File::exist?(projPath) and projPath.rindex('.xcodeproj')
        mainDir = "#{File::dirname(projPath)}/"
        fps = []
        for i in (1...ARGV.length)
            relativePath = ARGV[i]
            if relativePath.start_with?(mainDir)
                fps << relativePath.gsub(mainDir, '')
            else
                fps << relativePath
            end
        end
        projObj = ProjManager.new(projPath)
        result = projObj.handleFiles(fps)
        projObj.saveModify
        puts result
    end
end


